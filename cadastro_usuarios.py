from modulos.bd import connect_execute, read_table_df, listar_table, connect_params,listar_database,creat_database
from modulos.tables import table_geral, table_user
from werkzeug.security import generate_password_hash
from datetime import datetime


# # Cadastro Estabelecimento
# nome = 'salao dos milagres'
# endereco = 'Rua Frederico Rotulo,1046 - Apto 23 - Limeira-SP'
# tele = '19982874653'
# ativo = 1


# sql = '''INSERT INTO estabelecimentos_b (nome, endereco, telefone, ativo)
#          VALUES (%s, %s, %s, %s);
#        '''

# estab = connect_execute(sql, nome, endereco, tele, ativo)


# # Cadastro Usuário
# nome = 'Guilherme Theodoro da Silva'
# username = 'Guilhermetheo'
# email = 'guilherme.theodoro12@gmail.com'
# cpf = '43388362882'
# senha = generate_password_hash('teste')
# role = 'Master'
# telefone = '19982874653'
# data_cadastrado = datetime.now()
# ativo = True
# estab_id = estab

# sql = '''INSERT INTO usuarios_b (nome, username, email, cpf, senha, role, telefone, data_cadastro, estabelecimento_id, ativo)
#          VALUES ( %s, %s, %s, %s, %s,%s, %s, %s, %s, %s);
#     '''
# connect_execute(sql, nome, username, email, cpf, senha,
#                 role, telefone, data_cadastrado, estab_id, ativo)


# creat_database(username)
# connect_params(database=username)
table_user()

print(listar_table())
print(listar_database())


