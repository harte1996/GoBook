from modulos.bd import connect_execute, read_table_df, listar_table, connect_params, listar_database, creat_database, delete_table
from modulos.tables import table_geral, table_user
from werkzeug.security import generate_password_hash
from datetime import datetime


print(listar_table())
print(read_table_df('disponibilidade_profissional'))
# exit()
# delete_table('usuarios_b')
# delete_table('estabelecimentos_b')
# delete_table('agenda_excecao')
# delete_table('configuracao_agenda')
delete_table('disponibilidade_profissional')
# delete_table('estabelecimentos_b')
# delete_table('excecores_recorrentes')
# delete_table('profissional_b')
# delete_table('profissional_servicos')
# delete_table('servicos_b')

# print(read_table_df('usuarios_b'))
# table_geral()
# print(listar_table())

# delete_table('usuarios_b')
# delete_table('estabelecimentos_b')

# delete_table()

# sql = """UPDATE usuarios_b
#          SET username = 'inventario'
#          WHERE cpf = 43388362882"""

# connect_execute(sql)

# print(read_table_df('usuarios_b'))

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
# username = 'gobook'
# email = 'guilherme.theodoro12@gmail.com'
# cpf = '43388362882'
# senha = generate_password_hash('teste')
# role = 'Master'
# telefone = '19982874653'
# data_cadastrado = datetime.now()
# ativo = True
# try_test = False
# estab_id = 1

# sql = '''INSERT INTO usuarios_b (nome, username, email, cpf, senha, role, telefone, data_cadastro, estabelecimento_id, ativo, try_test)
#          VALUES ( %s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s);
#     '''
# connect_execute(sql, nome, username, email, cpf, senha,
#                 role, telefone, data_cadastrado, estab_id, ativo,try_test)


# print(read_table_df('usuarios_b'))
# creat_database(username.lower())
# print(listar_database())
# connect_params(database=username)
table_user()

# print(listar_table())
# print(listar_database())
