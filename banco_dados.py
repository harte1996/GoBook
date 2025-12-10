from modulos.bd import connect_consulta, read_table_df, connect_execute, listar_table, atualizar_table, delete_table
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd

print(listar_table())
table_user = False
table_profissional = False
table_servico =  False
table_relacionamento_servico_profissional = False
table_agenda = False

print(read_table_df('usuarios_b'))
print(read_table_df('estabelecimentos_b'))

exit()


if table_user:

    sql = '''CREATE TABLE IF NOT EXISTS usuarios_b (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100),
            username VARCHAR(50) UNIQUE,
            email VARCHAR(255),
            cpf VARCHAR(11),
            senha VARCHAR(255),
            role ENUM('Master', 'Admin', 'Cliente') DEFAULT 'Cliente',
            telefone VARCHAR(20),
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estabelecimento VARCHAR(255),
            ativo TINYINT DEFAULT 1
        );'''

    connect_execute(sql)

if table_profissional:

    sql = '''CREATE TABLE IF NOT EXISTS profissional_b (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            foto VARCHAR(255),
            criado_por INT,
            ativo TINYINT DEFAULT 1,
            FOREIGN KEY (criado_por) REFERENCES usuarios_b(id)
        );'''
    
    connect_execute(sql)

if table_servico:

    sql = '''
        CREATE TABLE IF NOT EXISTS servicos_b (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            tempo INT NOT NULL,
            foto VARCHAR(255)
        )
        '''
    connect_execute(sql)

if table_relacionamento_servico_profissional:

    sql = '''CREATE TABLE IF NOT EXISTS profissional_servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profissional_id INT NOT NULL,
    servico_id INT NOT NULL,
    preco DECIMAL(10,2) NULL,
    FOREIGN KEY (profissional_id) REFERENCES barbeiros_b(id) ON DELETE CASCADE,
    FOREIGN KEY (servico_id) REFERENCES servicos_b(id) ON DELETE CASCADE
    );'''

    connect_execute(sql)

if table_agenda:

    sql = ''' CREATE TABLE IF NOT EXISTS disponibilidade_profissional (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profissional_id INT NOT NULL,
    dia_semana INT NOT NULL,        -- 0=Segunda ... 6=Domingo
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    FOREIGN KEY (profissional_id)
        REFERENCES barbeiros_b(id)
        ON DELETE CASCADE);'''

    connect_execute(sql)

    sql = '''CREATE TABLE IF NOT EXISTS configuracao_agenda (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profissional_id INT NOT NULL,
    dias_aberta INT NOT NULL,

    FOREIGN KEY (profissional_id)
        REFERENCES barbeiros_b(id)
        ON DELETE CASCADE);'''
    
    connect_execute(sql)

    sql = '''CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profissional_id INT NOT NULL,
    cliente_nome VARCHAR(150) NOT NULL,
    telefone VARCHAR(15) DEFAULT NULL,
    data DATETIME NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    FOREIGN KEY (profissional_id)
        REFERENCES barbeiros_b(id)
        ON DELETE CASCADE
    );'''

    connect_execute(sql)

    sql = ''' CREATE TABLE IF NOT EXISTS agenda_excecao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profissional_id INT NOT NULL,
    data DATE NOT NULL,
    hora_inicio TIME DEFAULT NULL,
    hora_fim TIME DEFAULT NULL,
    fechado BOOLEAN DEFAULT 0,
    descricao VARCHAR(255) DEFAULT NULL,

    UNIQUE (profissional_id, data),

    FOREIGN KEY (profissional_id)
        REFERENCES barbeiros_b(id)
        ON DELETE CASCADE);'''

    connect_execute(sql)

    sql = ''' CREATE TABLE IF NOT EXISTS excecoes_recorrentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profissional_id INT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    descricao VARCHAR(255) DEFAULT NULL,

    FOREIGN KEY (profissional_id)
        REFERENCES barbeiros_b(id)
        ON DELETE CASCADE);'''
    
    connect_execute(sql)


# # print(servicos)
# print('agenda fixa')
# print(read_table_df('disponibilidade_profissional'))

# print('\nagenda config')
# print(read_table_df('configuracao_agenda'))

# print('\nexcecoes agenda')
# print(read_table_df('agenda_excecao'))

# print('\neventos agenda')
# print(read_table_df('evento_agenda'))

# print('\nExcecoes recorrent')
# print(read_table_df('excecoes_recorrentes'))

# print('\nAgendamentos')
# print(read_table_df('agendamentos'))

# '''CREATE INDEX idx_disp_barbeiro
# ON disponibilidade_profissional (profissional_id);

# CREATE INDEX idx_eventos_barbeiro
# ON agendamentos (profissional_id, data);

# CREATE INDEX idx_excecao_barbeiro
# ON agenda_excecao (profissional_id, data);'''