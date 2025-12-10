from modulos.bd import connect_consulta, connect_execute
import re


def check_user(username):
    # Pre arquivo
    cpf_cleaned = re.sub(r'[.-]', '', username)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # 1. Checa por CPF (11 dígitos, opcionalmente formatado com . e -)
    if len(cpf_cleaned) == 11 and cpf_cleaned.isdigit():
        query = "SELECT * FROM usuarios_b WHERE cpf = %s AND ativo = 1"
        username = cpf_cleaned

    elif re.fullmatch(email_pattern, username):
        query = "SELECT * FROM usuarios_b WHERE email = %s AND ativo = 1"

    # 3. Se não for nenhum dos anteriores, assume que é o nome de Usuário
    else:
        query = "SELECT * FROM usuarios_b WHERE username = %s AND ativo = 1"

    # Fazer checagem no banco de dados
    result = connect_consulta(query, username, dictonary=True)

    return result[0] if result else None


def table_geral():

    # Tabela do Usuário checar documentação #1 - GERAL
    sql_user = '''
    CREATE TABLE IF NOT EXISTS usuarios_b (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        cpf VARCHAR(11) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        role ENUM('Master', 'Admin', 'Cliente') DEFAULT 'Cliente' NOT NULL,
        telefone VARCHAR(20),
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        estabelecimento_id INT, 
        ativo TINYINT DEFAULT 1,
        FOREIGN KEY (estabelecimento_id) REFERENCES estabelecimentos_b(id) ON DELETE SET NULL
    );'''

    # Tabela do Estabelicimento checar documentação #2 - GERAL
    sql_estabelecimento = '''
        CREATE TABLE IF NOT EXISTS estabelecimentos_b (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            endereco VARCHAR(255),
            telefone VARCHAR(20),
            ativo TINYINT DEFAULT 1
        );'''

    connect_execute(sql_estabelecimento)
    connect_execute(sql_user)


def table_user():

    # Tabela do Profissional checar documentação #3 - USER
    sql_profissional = '''
        CREATE TABLE IF NOT EXISTS profissional_b (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            foto VARCHAR(255),
            criado_por INT NOT NULL,
            ativo TINYINT DEFAULT 1,
            estabelecimento_id INT NOT NULL,
            FOREIGN KEY (criado_por) REFERENCES usuarios_b(id),
            FOREIGN KEY (estabelecimento_id) REFERENCES estabelecimentos_b(id) ON DELETE CASCADE
        );'''

    connect_execute(sql_profissional)

    # Tabela do Serviço checar documentação #4 - USER
    sql_servico = '''
        CREATE TABLE IF NOT EXISTS servicos_b (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            tempo SMALLINT NOT NULL, -- Alterado para SMALLINT
            foto VARCHAR(255),
            estabelecimento_id INT NOT NULL,
            FOREIGN KEY (estabelecimento_id) REFERENCES estabelecimentos_b(id) ON DELETE CASCADE
        );'''
    connect_execute(sql_servico)

    # Tabela do Profissional checar documentação #5 - USER
    sql_relacionamento_servico_profissional = '''
        CREATE TABLE IF NOT EXISTS profissional_servicos (
            profissional_id INT NOT NULL,
            servico_id INT NOT NULL,
            preco DECIMAL(10,2) NULL,
            PRIMARY KEY (profissional_id, servico_id),
            FOREIGN KEY (profissional_id) REFERENCES profissional_b(id) ON DELETE CASCADE,
            FOREIGN KEY (servico_id) REFERENCES servicos_b(id) ON DELETE CASCADE
        );'''
    connect_execute(sql_relacionamento_servico_profissional)

    # Tabela do Disponib do Profissional checar documentação #6 - USER
    sql_disponibilidade = '''
        CREATE TABLE IF NOT EXISTS disponibilidade_profissional (
            id INT AUTO_INCREMENT PRIMARY KEY,
            profissional_id INT NOT NULL,
            dia_semana TINYINT NOT NULL CHECK (dia_semana BETWEEN 1 AND 7), -- 1=Segunda ... 7=Domingo
            hora_inicio TIME NOT NULL,
            hora_fim TIME NOT NULL,
            UNIQUE (profissional_id, dia_semana),
            FOREIGN KEY (profissional_id) REFERENCES profissional_b(id) ON DELETE CASCADE
        );'''
    connect_execute(sql_disponibilidade)

    # Tabela do Conf. agenda do Profissional checar documentação #7 - USER
    sql_configuracao_agenda = '''
        CREATE TABLE IF NOT EXISTS configuracao_agenda (
            id INT AUTO_INCREMENT PRIMARY KEY,
            profissional_id INT NOT NULL UNIQUE, -- Apenas uma configuracao por profissional
            dias_aberta INT NOT NULL,
            FOREIGN KEY (profissional_id) REFERENCES profissional_b(id) ON DELETE CASCADE
        );'''
    connect_execute(sql_configuracao_agenda)

    # Tabela de agendamentos checar documentação #8 - USER
    sql_agendamentos = '''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            profissional_id INT NOT NULL,
            servico_id INT NOT NULL,
            cliente_nome VARCHAR(150) NOT NULL,
            telefone VARCHAR(15) DEFAULT NULL,
            data DATETIME NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fim TIME NOT NULL,

            FOREIGN KEY (profissional_id) REFERENCES profissional_b(id) ON DELETE CASCADE,
            FOREIGN KEY (servico_id) REFERENCES servicos_b(id) ON DELETE RESTRICT,
        );'''
    connect_execute(sql_agendamentos)

    # 9. Tabela de Exceção de Agenda Diária
    sql_agenda_excecao = '''
        CREATE TABLE IF NOT EXISTS agenda_excecao (
            id INT AUTO_INCREMENT PRIMARY KEY,
            profissional_id INT NOT NULL,
            data DATE NOT NULL,
            hora_inicio TIME DEFAULT NULL,
            hora_fim TIME DEFAULT NULL,
            fechado BOOLEAN DEFAULT 0,
            descricao VARCHAR(255) DEFAULT NULL,

            UNIQUE (profissional_id, data),
            FOREIGN KEY (profissional_id) REFERENCES profissional_b(id) ON DELETE CASCADE
        );'''
    connect_execute(sql_agenda_excecao)

    # 10. Tabela de Exceções Recorrentes (para feriados fixos, etc. - Ajuste na sua estrutura)
    sql_excecoes_recorrentes = '''
        CREATE TABLE IF NOT EXISTS excecoes_recorrentes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            profissional_id INT NOT NULL,
            descricao VARCHAR(255) DEFAULT NULL,
            hora_inicio TIME NOT NULL,
            hora_fim TIME NOT NULL,

            FOREIGN KEY (profissional_id) REFERENCES profissional_b(id) ON DELETE CASCADE
        );'''
    connect_execute(sql_excecoes_recorrentes)
