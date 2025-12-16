from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from modulos.bd import connect_execute, connect_consulta
from routes.agenda import agenda_disponivel
from urllib.parse import quote
from datetime import datetime, timedelta


client_bp = Blueprint('cliente', __name__)


@client_bp.route('/client')
def client():
    # Exemplo: substitua pelas suas consultas reais
    profissional = connect_consulta(
        'SELECT id, nome, foto FROM profissional_b', dictonary=True)
    servicos = connect_consulta(
        'SELECT id, nome, tempo, valor, foto FROM servicos_b', dictonary=True)
    return render_template('cliente_agendar.html', profissional=profissional, servicos=servicos)


@client_bp.route('/client/horarios')
def client_horarios():
    data = request.args.get('data')
    profissional_id = request.args.get('profissional')
    servico_id = request.args.get('servico')

    data = datetime.strptime(data, '%Y-%m-%d')

    # Agenda disponivel do profissional
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
    
    agenda = agenda_disponivel(data,agenda_fixa,excecoes,ocupados,excecoes_recorrent)

    # Consulta o servico para definir o tempo
    service = connect_consulta('''
    SELECT tempo
    FROM servicos_b
    WHERE id=%s                                              
    ''', servico_id, dictonary=True)
    tempo_service = service[0]['tempo']

    hrs_disp = []

    # Loop para definir os horários disponiveis
    for a in agenda:

        if a['evento'] != 'normal':
            continue

        inicio = (datetime.combine(a['data'], a['hora_inicio']))
        fim = (datetime.combine(a['data'], a['hora_fim']))

        # Define o formato de tempo
        time_dif = fim - inicio
        time_dif = (int(time_dif.seconds / 60))

        if time_dif > tempo_service:
            # quebrar_intervalo_services(inicio, fim, tempo_service)
            time_atual = inicio
            while time_atual < fim:
                hrs_disp.append(time_atual.time().isoformat()[:5])
                time_atual = time_atual + timedelta(minutes=tempo_service)

    return render_template('partials/horarios_client.html', horarios=hrs_disp)


@client_bp.route('/client/confirmar/', methods=['POST'])
def client_confirmar():
    nome = request.form['nome']
    telefone = request.form['telefone']
    profissional = request.form['profissional_nome']
    profissional_id = request.form['profissional']
    servico = request.form['servico_nome']
    servico_id = request.form['servico']
    data = request.form['data']
    hora = request.form['horario']

    # Transformar em datatime
    data = datetime.strptime(data, '%Y-%m-%d')
    hora = datetime.strptime(hora, '%H:%M')

    # Consulta o servico para definir o tempo
    service = connect_consulta('''
    SELECT tempo
    FROM servicos_b
    WHERE id=%s                                              
    ''', servico_id, dictonary=True)
    tempo_service = service[0]['tempo']

    hora_fim = hora + timedelta(minutes=int(tempo_service))

    agendar = connect_execute("""
    INSERT INTO agendamentos
    (profissional_id, cliente_nome, telefone, data, hora_inicio, hora_fim,servico_id)
    VALUES (%s, %s, %s, %s, %s, %s,%s)
    """,
                    profissional_id,
                    nome,
                    telefone,
                    data.date(),
                    hora,
                    hora_fim,
                    servico_id
                    )

    if not agendar:
        return render_template('error.html')

    msg = f"""
    Olá! Acabei de agendar meu horário ✅


    📅 Data: {data.strftime('%d/%m/%Y')}
    ⏰ Horário: {hora.time().isoformat()}
    💈 profissional: {profissional}
    ✂️ Serviço: {servico}


    Meu nome: {nome}
    Telefone: {telefone}
    """

    link = 'https://wa.me/19982874653?text=' + quote(msg)

    return jsonify({'redirect': link})


@client_bp.route('/client/servicos/<int:profissional_id>')
def servicos_por_profissional(profissional_id):
    sql = """
        SELECT 
            s.id,
            s.nome,
            s.foto,
            bs.preco
        FROM profissional_servicos bs
        JOIN servicos_b s ON s.id = bs.servico_id
        WHERE bs.profissional_id = %s
    """
    servicos = connect_consulta(sql, profissional_id, dictonary=True)
    return render_template('partials/_servicos_cards.html', servicos=servicos)

