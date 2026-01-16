from modulos.bd import connect_execute, read_table_df, listar_table, connect_params, listar_database, creat_database, delete_table
from modulos.tables import table_geral, table_user
from werkzeug.security import generate_password_hash
from datetime import datetime


sql = '''UPDATE gobook.usuarios_b
         SET slug = 'guilhermetheo'
         WHERE cpf = 43388362882
         '''

sql = connect_execute(sql)
print(read_table_df('agendamentos'))

# print(listar_table())
# delete_table('Guilhermetheo.configuracao_agenda')
# delete_table('Guilhermetheo.agenda_excecao')
# delete_table('Guilhermetheo.excecoes_recorrentes')
# delete_table('Guilhermetheo.disponibilidade_profissional')
# delete_table('Guilhermetheo.profissional_servicos')
# delete_table('Guilhermetheo.agendamentos')
# delete_table('Guilhermetheo.profissional_b')
# delete_table('Guilhermetheo.servicos_b')
# delete_table('usuarios_b')
# delete_table('estabelecimentos_b')

# table_geral()

# Cadastro Estabelecimento
# nome = 'salao dos milagres'
# endereco = 'Rua Frederico Rotulo,1046 - Apto 23 - Limeira-SP'
# tele = '19982874653'
# ativo = 1
# sql = '''INSERT INTO estabelecimentos_b (nome, endereco, telefone, ativo)
#          VALUES (%s, %s, %s, %s);
#        '''
# estab = connect_execute(sql, nome, endereco, tele, ativo)
# Cadastro Usuário
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

# creat_database(username.lower())
# connect_params(database=username)
# table_user()
# print(listar_table())
# print(listar_database())
