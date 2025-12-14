from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta, time
from modulos.bd import connect_execute, connect_consulta
from routes.auth import admin_required
import pandas as pd


agenda_bp = Blueprint('agenda', __name__)


def quebrar_intervalo(dt_inicio, dt_fim, bloqueios, tipo):
    """
    Quebra um intervalo normal em:
    - normal
    - bloqueios (excecao ou ocupado)
    """
    slots = []
    atual = dt_inicio

    for b in bloqueios:
        b_ini = datetime.combine(b['data'], time()) + b['hora_inicio']
        b_fim = datetime.combine(b['data'], time()) + b['hora_fim']

        if b_fim <= atual or b_ini >= dt_fim:
            continue

        if atual < b_ini:
            slots.append((atual, b_ini, 'normal', 'livre'))


        if tipo == 'ocupado':
            slots.append(
                (b_ini, b_fim, tipo, f"{b['cliente_nome']} \n{b['telefone']}" if 'cliente_nome' in b.keys() else 'NA'))
            atual = b_fim

        else:
            slots.append(
                (b_ini, b_fim, tipo, b['descricao'] if 'descricao' in b.keys() else 'NA'))
            atual = b_fim

    if atual < dt_fim:
        slots.append((atual, dt_fim, 'normal', 'livre'))

    return slots


def agenda_disponivel(date, agenda_fixa, excecoes, ocupados, excecoes_recorrent):

    # =========================
    # MAPAS
    # =========================

    excecao_fechado = [e for e in excecoes if e['fechado']]

    # =========================
    # LOOP PRINCIPAL
    # =========================

    agenda_dia = []
    slots = []


    # Verificar se o dia está na agenda de disponivel
    disp = next(
    (d for d in agenda_fixa if d['dia_semana'] == date.weekday()),
    None) # <-- Valor Padrão caso não encontre nada

    if disp:

        inicio_dia = datetime.combine(date.date(), time()) + disp['hora_inicio'] 
        inicio_dia = inicio_dia if inicio_dia > datetime.now() else datetime.now(
        ).replace(minute=0 if datetime.now().minute < 30 else 30, second=0)
        fim_dia = datetime.combine(date.date(), time()) + disp['hora_fim'] 

        # -------------------------
        # DIA FECHADO
        # -------------------------
        if date.date() in [e['data'] for e in excecao_fechado]:
            agenda_dia.append({
                'data': date.date(),
                'hora_inicio': inicio_dia.time(),
                'hora_fim': fim_dia.time(),
                'evento': 'fechado',
                'descricao': [e['descricao'] for e in excecao_fechado if e['data'] == date.date()]
            })
            return agenda_dia

        # -------------------------
        # INÍCIO NORMAL DO DIA
        # -------------------------
        slots = [(inicio_dia, fim_dia, 'normal', 'livre')]

        # -------------------------
        # QUEBRA POR EXCEÇÕES RECORRENTES
        # -------------------------
        for e in excecoes_recorrent:
            e['data'] = date.date()
        excs_r = [e for e in excecoes_recorrent]

        novos = []
        for ini, fim, tipo, descricao in slots:
            novos.extend(quebrar_intervalo(ini, fim, excs_r, 'excecao_rec'))
        slots = novos

        # -------------------------
        # QUEBRA POR EXCEÇÕES
        # -------------------------
        excs = [e for e in excecoes if e['data'] ==
                date.date() and not e['fechado']]

        novos = []
        for ini, fim, tipo, descricao in slots:
            if tipo != 'normal':
                novos.append((ini, fim, tipo, descricao))
            else:
                novos.extend(quebrar_intervalo(ini, fim, excs, 'excecao'))
        slots = novos


    # -------------------------
    # QUEBRA POR OCUPADOS
    # -------------------------
    ocps = [o for o in ocupados if o['data'].date() ==
            date.date()] if ocupados else []

    novos = []
    for ini, fim, tipo, descricao in slots:
        if tipo != 'normal':
            novos.append((ini, fim, tipo, descricao))
        else:
            novos.extend(quebrar_intervalo(ini, fim, ocps, 'ocupado'))

    slots = novos

    # -------------------------
    # SALVAR
    # -------------------------
    for ini, fim, tipo, descricao in slots:
        agenda_dia.append({
            'data': ini.date(),
            'hora_inicio': ini.time(),
            'hora_fim': fim.time(),
            'evento': tipo,
            'descricao': descricao
        })

    return agenda_dia


# ===========================
# TELA PRINCIPAL DA AGENDA
# ===========================
@agenda_bp.route('/agenda')
@admin_required
def agenda_profissional():
    profissional = connect_consulta(
        "SELECT id, nome FROM gobook.profissional_b ORDER BY nome", dictonary=True
    )
    return render_template(
        'agenda_profissional.html',
        profissional=profissional
    )


# ===========================
# SALVAR DISPONIBILIDADE FIXA
# ===========================
#

@agenda_bp.route('/salvar-disponibilidade', methods=['POST'])
@admin_required
def salvar_disponibilidade():
    print('entrei')
    data = request.get_json()

    profissional_id = data['profissional_id']
    dias = data['dias']
    hora_inicio = data['hora_inicio']
    hora_fim = data['hora_fim']
    dias_aberta = int(data['dias_aberta'])
    excecoes = data.get('excecoes', [])

    # ✅ Remove disponibilidade antiga
    connect_execute(
        "DELETE FROM disponibilidade_profissional WHERE profissional_id=%s",
        profissional_id
    )

    # ✅ Salva nova disponibilidade
    for dia in dias:
        print(profissional_id)
        print(int(dia))
        print(hora_inicio)
        print(hora_fim)
        connect_execute("""
            INSERT INTO disponibilidade_profissional
            (profissional_id, dia_semana, hora_inicio, hora_fim)
            VALUES (%s, %s, %s, %s)
        """, profissional_id, int(dia), hora_inicio, hora_fim)
        

    # ✅ Configuração geral
    connect_execute("""
        DELETE FROM configuracao_agenda
        WHERE profissional_id=%s
    """, profissional_id)

    connect_execute("""
        INSERT INTO configuracao_agenda
        (profissional_id, dias_aberta)
        VALUES (%s, %s)
    """, profissional_id, dias_aberta)

    # ✅ Remove exceções recorrentes antigas
    connect_execute("""
        DELETE FROM excecoes_recorrentes
        WHERE profissional_id=%s
    """, profissional_id)

    # ✅ Salva novas exceções recorrentes
    for ex in excecoes:
        if ex['hora_inicio'] and ex['hora_fim']:
            connect_execute("""
                INSERT INTO excecoes_recorrentes
                (profissional_id, hora_inicio, hora_fim, descricao)
                VALUES (%s, %s, %s, %s)
            """,
                            profissional_id,
                            ex['hora_inicio'],
                            ex['hora_fim'],
                            ex.get('descricao')
                            )

    return jsonify({"status": "ok"})



# ===========================
# EVENTOS DO FULLCALENDAR
# ===========================
@agenda_bp.route('/agenda/eventos')
@admin_required
def eventos_agenda():

    profissional_id = request.args.get('profissional_id')

    # =========================
    # FUNÇÕES AUXILIARES
    # =========================

    def color_for_evento(evento):

        EVENTO_DISPONIVEL = "#389268"
        EVENTO_OCUPADO = "#ca3e4c"
        EVENTO_EXCECAO = "#f0ad4e"
        EVENTO_FECHADO = "#6c757d"

        if evento == 'normal':
            return EVENTO_DISPONIVEL
        elif evento == 'ocupado':
            return EVENTO_OCUPADO
        elif evento == 'excecao':
            return EVENTO_EXCECAO
        elif evento == 'fechado':
            return EVENTO_FECHADO

    # =========================
    # DADOS INICIAIS
    # =========================

    config = connect_consulta("""
    SELECT dias_aberta
    FROM configuracao_agenda
    WHERE profissional_id=%s
    """, profissional_id, dictonary=True)

    print(config)

    config = config[0] if len(config) > 0 else []
    print(config)

    agenda_fixa = connect_consulta("""
    SELECT dia_semana, hora_inicio, hora_fim
    FROM disponibilidade_profissional
    WHERE profissional_id=%s
    """, profissional_id, dictonary=True)

    excecoes = connect_consulta("""
    SELECT data, hora_inicio, hora_fim, fechado, descricao
    FROM agenda_excecao
    WHERE profissional_id=%s
    """, profissional_id, dictonary=True)

    ocupados = connect_consulta("""
    SELECT *
    FROM agendamentos
    WHERE profissional_id=%s
    """, profissional_id, dictonary=True)

    excecoes_recorrent = connect_consulta("""
    SELECT  hora_inicio, hora_fim, descricao
    FROM excecoes_recorrentes
    WHERE profissional_id=%s
    """, profissional_id, dictonary=True)
    
    dias_aberta = int(config['dias_aberta']) if len(config) > 0 else 0

    # =========================
    # LOOP PRINCIPAL
    # =========================

    data_atual = datetime.now()
    data_final = datetime.now() + timedelta(days=dias_aberta)
    data_final = data_final.replace(hour=23, minute=59)
    agenda_dia = []

    while data_atual < data_final:

        agenda_dia.extend(agenda_disponivel(data_atual, agenda_fixa, excecoes, ocupados, excecoes_recorrent))
        data_atual = data_atual + timedelta(days=1)

    eventos = []

    for e in agenda_dia:
        if e['evento'] == 'fechado':
            eventos.append({
                'title': e['descricao'],
                'start': str(e['data']),
                'allDay': True,
                'display': 'background',
                'color': color_for_evento(e['evento'])
            })
        else:
            eventos.append({
                'title': e['descricao'].capitalize(),
                'start': f"{e['data']}T{e['hora_inicio'].isoformat()}",
                'end':   f"{e['data']}T{e['hora_fim'].isoformat()}",
                'allDay': False,
                'color': color_for_evento(e['evento']),
                'extendedProps': {
                    'tipo': e['descricao']
                }
            })

    return jsonify(eventos)


# ===========================
# SALVAR EXCEÇÃO DE AGENDA
# ===========================
@agenda_bp.route('/excecao', methods=['POST'])
@admin_required
def salvar_excecao():

    data = request.get_json()

    profissional_id = data['profissional_id']
    data_excecao = data['data']
    fechado = data['fechado']
    hora_inicio = data.get('hora_inicio')
    hora_fim = data.get('hora_fim')
    descricao = data['descricao']

    # cria exceção nova
    connect_execute("""
        INSERT INTO agenda_excecao
        (profissional_id, data, hora_inicio, hora_fim, fechado, descricao)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
                    profissional_id,
                    data_excecao,
                    hora_inicio,
                    hora_fim,
                    fechado,
                    descricao
                    )

    return jsonify({"status": "ok"})

# ===========================
# REMOVER EXCEÇÃO
# ===========================


@agenda_bp.route('/excecao/remover', methods=['POST'])
@admin_required
def remover_excecao():
    data = request.get_json()

    connect_execute("""
        DELETE FROM agenda_excecao 
        WHERE profissional_id=%s AND data=%s
    """, data['profissional_id'], data['data'])

    return jsonify({"status": "ok"})
