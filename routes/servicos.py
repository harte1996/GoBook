from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import uuid
from modulos.bd import connect_execute, connect_consulta
from routes.cadastro import sanitizar_email
from routes.auth import login_required, admin_required
from PIL import Image

servicos_bp = Blueprint('servicos', __name__)
UPLOAD_FOLDER = "static/uploads/"


def salvar_imagem_como_jpg(file, destino):
    img = Image.open(file)

    # Converte para RGB (evita erro com PNG/WEBP com transparência)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.save(destino, "JPEG", quality=85)


@servicos_bp.route('/servicos/cadastrar', methods=['GET'])
def pagina_cadastrar_servico():
    sql = "SELECT id, nome, valor, foto, tempo FROM servicos_b ORDER BY nome DESC"
    servicos = connect_consulta(sql, dictonary=True)
    servicos = [] if servicos is None else servicos
    return render_template('cadastrar_servico.html', servicos=servicos)


@servicos_bp.route('/servicos/cadastrar/ajax', methods=['POST'])
@admin_required
def cadastrar_servico():
    try:
        nome = request.form.get('nome')
        valor = request.form.get('valor')
        foto = request.files.get('foto')
        tempo = request.form.get('tempo')
        estab = session['estabelecimento_id']

        if not nome or not valor:
            return jsonify({"status": "error", "message": "Preencha todos os campos obrigatórios!"}), 400

        # Pasta do usuário logado
        id_user = session.get('user_id')
        sql = "SELECT email FROM usuarios_b WHERE id=%s"
        email = connect_consulta(sql, id_user, dictonary=True)[0]['email']
        email = sanitizar_email(email)
        caminho_pasta = os.path.join(UPLOAD_FOLDER, email, 'fotos_servicos')

        os.makedirs(caminho_pasta, exist_ok=True)

        # salvar imagem
        filename = None
        if foto:
            filename = f"{uuid.uuid4()}.jpg"
            file = os.path.join(caminho_pasta, filename)
            salvar_imagem_como_jpg(foto, file)

        # salvar no banco
        sql_insert = '''INSERT INTO servicos_b (nome, valor, foto, tempo,estabelecimento_id) VALUES (%s, %s, %s, %s,%s)'''
        connect_execute(sql_insert, nome, float(valor),
                        f'{email}/fotos_servicos/{filename}', tempo, estab)

        return jsonify({"status": "success", "message": "Serviço cadastrado com sucesso!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@servicos_bp.route('/servicos/excluir/<int:id>', methods=['DELETE'])
@admin_required
def excluir_servico(id):
    try:
        # Buscar a foto antes de excluir
        sql_foto = "SELECT foto FROM servicos_b WHERE id=%s"
        dados = connect_consulta(sql_foto, id, dictonary=True)

        if not dados:
            return jsonify({"status": "error", "message": "Serviço não encontrado"}), 404

        foto = dados[0]["foto"]

        # Excluir o serviço
        sql_delete = "DELETE FROM servicos_b WHERE id=%s"
        connect_execute(sql_delete, id)

        # Excluir a foto do disco
        if foto and os.path.exists(f"static/uploads/{foto}"):
            os.remove(f"static/uploads/{foto}")

        return jsonify({"status": "success", "message": "Serviço excluído com sucesso!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@servicos_bp.route('/servicos/editar/<int:id>', methods=['POST'])
@admin_required
def editar_servico(id):
    try:
        nome = request.form.get("nome")
        valor = request.form.get("valor")
        foto = request.files.get("foto")
        tempo = request.form.get("tempo")
        estab = session['estabelecimento_id']

        if not nome or not valor:
            return jsonify({"status": "error", "message": "Preencha todos os campos obrigatórios!"})

        # Buscar foto atual
        sql_foto = "SELECT foto FROM servicos_b WHERE id=%s"
        dados = connect_consulta(sql_foto, id, dictonary=True)
        foto_atual = dados[0]["foto"] if dados else None

        # Se enviar nova foto → salva e apaga a antiga
        filename = foto_atual
        if foto:
            ext = foto.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            foto.save(os.path.join(UPLOAD_FOLDER, filename))

            if foto_atual and os.path.exists(f"static/uploads/{foto_atual}"):
                os.remove(f"static/uploads/{foto_atual}")

        sql_update = """
            UPDATE servicos_b
            SET nome=%s, valor=%s, foto=%s, tempo=%s, estabelecimento_id=%s,
            WHERE id=%s
        """
        connect_execute(sql_update, nome, float(
            valor), filename, tempo, estab, id)

        return jsonify({"status": "success", "message": "Serviço atualizado com sucesso!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
