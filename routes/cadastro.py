import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from modulos.bd import connect_execute, connect_consulta, read_table_df
from routes.auth import admin_required
from datetime import datetime


cadastro_bp = Blueprint('cadastro', __name__)

UPLOAD_FOLDER = 'static/uploads'


def sanitizar_email(email: str):
    return email.replace("@", "_").replace(".", "_")


@cadastro_bp.route('/cadastrar_profissional', methods=['GET', 'POST'])
@admin_required
def cadastrar_profissional():

    # Buscar serviços cadastrados
    servicos = connect_consulta(
        "SELECT id, nome, valor FROM servicos_b", dictonary=True) or []

    if request.method == 'POST':

        nome = request.form.get('nome')
        email_profissional = request.form.get('email')
        servicos_selecionados = request.form.getlist('servicos[]') or []
        foto = request.files.get('foto')

        # ---- Validação simples ----
        if not nome or not email_profissional:
            flash("Nome e e-mail são obrigatórios.", "warning")
            return redirect(url_for('cadastro.cadastrar_profissional'))

        # ---- Pasta do usuário logado ----
        id_user = session.get('user_id')
        email_usuario = connect_consulta(
            "SELECT email FROM usuarios_b WHERE id=%s",
            id_user,
            dictonary=True
        )[0]['email']

        pasta_usuario = sanitizar_email(email_usuario)
        caminho_pasta = os.path.join(
            UPLOAD_FOLDER, pasta_usuario, 'fotos_profissional')
        os.makedirs(caminho_pasta, exist_ok=True)

        # ---- Salvar foto ----
        foto_nome = None
        if foto and foto.filename:
            ext = foto.filename.rsplit('.', 1)[-1].lower()
            foto_nome = f"{uuid.uuid4()}.{ext}"
            foto.save(os.path.join(caminho_pasta, foto_nome))

        # ---- Inserir profissional ----
        try:
            sql = """
                INSERT INTO profissional_b (nome, email, foto, criado_por)
                VALUES (%s, %s, %s, %s)
            """
            id_profissional = connect_execute(
                sql,
                nome,
                email_profissional,
                f"{pasta_usuario}/fotos_profissional/{foto_nome}" if foto_nome else None,
                id_user
            )
        except Exception as e:
            if "Duplicate entry" in str(e):
                flash("Este e-mail já está cadastrado para outro profissional!", "danger")
            else:
                flash("Erro ao cadastrar profissional.", "danger")
            return redirect(url_for('cadastro.cadastrar_profissional'))

        # ---- Inserir serviços selecionados ----
        for servico_id in servicos_selecionados:
            preco = connect_consulta(
                'SELECT valor FROM servicos_b WHERE id=%s', servico_id)[0][0]
            connect_execute(
                "INSERT INTO profissional_servicos (profissional_id, servico_id, preco) VALUES (%s, %s, %s)",
                id_profissional, servico_id, preco
            )

        flash("profissional cadastrado com sucesso!", "success")
        return redirect(url_for('cadastro.cadastrar_profissional'))

    return render_template("profissional_cadastrar.html", servicos=servicos)


@cadastro_bp.route('/listar')
def listar_profissional():
    sql = """
        SELECT b.id AS id, b.nome, b.email, b.foto,
               s.id AS servico_id, s.nome AS servico_nome,
               COALESCE(bs.preco, s.valor) AS preco
        FROM profissional_b b
        LEFT JOIN profissional_servicos bs ON bs.profissional_id = b.id
        LEFT JOIN servicos_b s ON s.id = bs.servico_id
        ORDER BY b.id
    """

    dados = connect_consulta(sql, dictonary=True) or []

    profissional = {}

    for row in dados:
        bid = row["id"]

        if bid not in profissional:
            profissional[bid] = {
                "id": row["id"],
                "nome": row["nome"],
                "email": row["email"],
                "foto": row["foto"],
                "servicos": []
            }

        # Evita adicionar serviços nulos
        if row["servico_id"]:
            profissional[bid]["servicos"].append({
                "id": row["servico_id"],
                "nome": row["servico_nome"],
                "preco": row["preco"]
            })

    return render_template("profissional_listar.html", profissional=profissional.values())


@cadastro_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_profissional(id):

    # Buscar profissional
    profissional = connect_consulta(
        "SELECT * FROM profissional_b WHERE id=%s", id, dictonary=True)[0]

    # Buscar todos serviços
    todos_servicos = connect_consulta(
        "SELECT * FROM servicos_b ORDER BY nome ASC", dictonary=True)

    # Buscar serviços do profissional
    sql = """
        SELECT servico_id, preco
        FROM profissional_servicos
        WHERE profissional_id = %s
    """
    servicos_profissional = connect_consulta(sql, id, dictonary=True)

    
    servicos_ids = [s["servico_id"] for s in servicos_profissional]

    # Dicionário: servico_id -> preco
    servicos_precos = {s["servico_id"]: s["preco"]
                       for s in servicos_profissional if s}

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        servicos_selecionados = request.form.getlist("servicos[]")

        foto = request.files.get("foto")
        nome_foto = profissional["foto"]

        if foto:
            nome_foto = f"{uuid.uuid4().hex}_{secure_filename(foto.filename)}"
            foto.save(os.path.join("static/uploads", nome_foto))

        # Atualizar profissional
        connect_execute("""
            UPDATE profissional_b SET nome=%s, email=%s, foto=%s WHERE id=%s
        """, nome, email, nome_foto, id)

        # Atualizar serviços vinculados
        connect_execute(
            "DELETE FROM profissional_servicos WHERE profissional_id=%s", id)

        for serv_id in servicos_selecionados:
            connect_execute("""
                INSERT INTO profissional_servicos (profissional_id, servico_id, preco)
                VALUES (%s, %s, (
                    SELECT valor FROM servicos_b WHERE id=%s
                ))
            """, id, serv_id, serv_id)

        return redirect(url_for("cadastro.listar_profissional"))

    return render_template(
        "profissional_editar.html",
        profissional=profissional,
        todos_servicos=todos_servicos,
        servicos_do_profissional_ids=servicos_ids,
        servicos_precos=servicos_precos
    )


@cadastro_bp.route('/profissional/excluir/<int:id>', methods=['POST'])
@admin_required
def excluir_profissional(id):

    # Verificar se tem agendamentos ativos (se você tiver tabela)
    ag = read_table_df("agendamentos").loc[ag['data'] > datetime.now()]
    if not ag.empty and id in ag["profissional_id"].values:
        flash("Este profissional possui agendamentos e não pode ser excluído.", "danger")
        return redirect(url_for("cadastro.listar_profissional"))

    df = read_table_df("profissional_b")

    if id not in df["id"].values:
        flash("Profissional não encontrado!", "danger")
        return redirect(url_for("cadastro.listar_profissional"))
    
    sql = 'DELETE FROM profissional_servicos WHERE profissional_id=%s'
    connect_execute(sql, id)

    sql = 'DELETE FROM profissional_b WHERE id=%s'
    connect_execute(sql, id)

    flash("Profissional excluído com sucesso!", "success")
    return redirect(url_for("cadastro.listar_profissional"))


@cadastro_bp.route("/alterar_preco", methods=["POST"])
def alterar_preco():
    data = request.get_json()
 
    profissional = data["profissional_id"]
    servico = data["servico_id"]
    preco = data["preco"]

    sql = """
        UPDATE profissional_servicos
        SET preco = %s
        WHERE profissional_id = %s AND servico_id = %s
    """

    connect_execute(sql, preco, profissional, servico)

    return jsonify({"status": "ok"})
