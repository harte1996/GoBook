# 📚 Documentação do Esquema de Banco de Dados

Este documento detalha o esquema do banco de dados utilizado para gerenciar usuários, profissionais, serviços e agendamentos.

## 1. `usuarios_b` (Usuários da aplicação)

Contém dados de todos os usuários do sistema, incluindo clientes, administradores e masters.

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | ID do usuário. |
| **nome** | `VARCHAR(100)` | `NOT NULL` | Nome completo. |
| **username** | `VARCHAR(50)` | `UNIQUE`, `NOT NULL` | Nome de usuário único para login. |
| **email** | `VARCHAR(255)` | `UNIQUE`, `NOT NULL` | E-mail. |
| **cpf** | `VARCHAR(11)` | `UNIQUE` , `NOT NULL` | CPF (somente 11 dígitos). |
| **senha** | `VARCHAR(255)` | `NOT NULL` | Senha (hash). |
| **role** | `ENUM` | `DEFAULT 'Cliente'`, `NOT NULL` | Nível de acesso: 'Master', 'Admin', 'Cliente'. |
| **telefone** | `VARCHAR(20)` | | Telefone/Celular. |
| **data_cadastro** | `TIMESTAMP` | `DEFAULT` | `CURRENT_TIMESTAMP` |  | Data de criação do usuário. |  
| **estabelecimento_id** | `INT` | `FOREIGN KEY (estabelecimentos_b.id)` | Estabelecimento principal do usuário (Masters/Admins). |
| **ativo** | `TINYINT` | `DEFAULT 1` | Status (1=Ativo, 0=Inativo). |

Essa tabela vai ser compartilhada com todos os usuários.
---



## 2. `estabelecimentos_b` (Estabelecimentos)

Gerencia as unidades ou locais onde os serviços são prestados. Essencial para suportar múltiplos locais.

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | Identificador único do estabelecimento. |
| **nome** | `VARCHAR(150)` | `NOT NULL` | Nome comercial do estabelecimento. |
| **endereco** | `VARCHAR(255)` | | Endereço físico. |
| **telefone** | `VARCHAR(20)` | | Telefone de contato. |
| **ativo** | `TINYINT` | `DEFAULT 1` | Status do estabelecimento (1=Ativo, 0=Inativo). |

Essa tabela vai ser compartilhada com todos os usuários.
---


Tabelas a seguir vai ser aberta a cada usuário novo para manter os dados isolados para uma segurança dos dados.

---

## 3. `profissional_b` (Profissionais)

Contém dados dos colaboradores que prestam serviços agendáveis.

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | ID do profissional. |
| **nome** | `VARCHAR(100)` | `NOT NULL` | Nome do profissional. |
| **email** | `VARCHAR(100)` | `UNIQUE` | E-mail de contato. |
| **foto** | `VARCHAR(255)` | | URL/caminho da foto. |
| **criado_por** | `INT` | `NOT NULL`, `FOREIGN KEY (usuarios_b.id)` | Usuário que criou o registro (auditoria). |
| **estabelecimento_id** | `INT` | `NOT NULL`, `FOREIGN KEY (estabelecimentos_b.id)` | Estabelecimento ao qual o profissional está ligado. |
| **ativo** | `TINYINT` | `DEFAULT 1` | Status. |

---

## 4. `servicos_b` (Serviços)

Catálogo de serviços oferecidos.

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | ID do serviço. |
| **nome** | `VARCHAR(100)` | `NOT NULL` | Nome do serviço (ex: "Corte Feminino"). |
| **valor** | `DECIMAL(10,2)` | `NOT NULL` | Preço base do serviço. |
| **tempo** | `SMALLINT` | `NOT NULL` | Duração padrão do serviço em **minutos**. |
| **foto** | `VARCHAR(255)` | | Imagem do serviço. |
| **estabelecimento_id** | `INT` | `NOT NULL`, `FOREIGN KEY (estabelecimentos_b.id)` | Estabelecimento que oferece este serviço. |

---

## 5. `profissional_servicos` (Relação N:N)

Associação entre profissionais e os serviços que eles estão aptos a realizar.

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **profissional_id** | `INT` | `PRIMARY KEY`, `FOREIGN KEY (profissional_b.id)` | ID do profissional. |
| **servico_id** | `INT` | `PRIMARY KEY`, `FOREIGN KEY (servicos_b.id)` | ID do serviço. |
| **preco** | `DECIMAL(10,2)` | `NULL` | Preço específico cobrado por este profissional para este serviço (sobrescreve o `valor` de `servicos_b`). |

---

## 6. Tabelas de Agenda

### `disponibilidade_profissional`

Define a grade de horários **recorrentes** de trabalho do profissional.

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | ID da disponibilidade. |
| **profissional_id**| `INT` | `NOT NULL`, `FOREIGN KEY` | Profissional. |
| **dia_semana** | `TINYINT` | `NOT NULL`, `UNIQUE(profissional_id, dia_semana)` | Dia da semana (1=Segunda, ..., 7=Domingo). |
| **hora_inicio** | `TIME` | `NOT NULL` | Horário de início do expediente. |
| **hora_fim** | `TIME` | `NOT NULL` | Horário de fim do expediente. |

### `configuracao_agenda`

Define regras globais para a agenda de um profissional.

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | ID da configuração. |
| **profissional_id**| `INT` | `NOT NULL`, `UNIQUE`, `FOREIGN KEY` | Profissional. |
| **dias_aberta** | `INT` | `NOT NULL` | Quantos dias à frente a agenda deve estar aberta para agendamentos. |

---

## 7. `agendamentos` (Reservas)

Registra cada reserva efetuada.

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | ID do agendamento. |
| **profissional_id**| `INT` | `NOT NULL`, `FOREIGN KEY` | Profissional reservado. |
| **servico_id** | `INT` | `NOT NULL`, `FOREIGN KEY` | Serviço reservado. |
| **cliente_id** | `INT` | `NULL`, `FOREIGN KEY (usuarios_b.id)` | ID do cliente (se tiver conta). |
| **cliente_nome** | `VARCHAR(150)` | `NOT NULL` | Nome do cliente (usado se `cliente_id` for NULL). |
| **telefone** | `VARCHAR(15)` | `DEFAULT NULL` | Telefone de contato. |
| **data_hora_inicio**| `DATETIME` | `NOT NULL` | Data e hora exata de início da reserva. |
| **hora_fim** | `TIME` | `NOT NULL` | Hora de término da reserva. |

---

## 8. Tabelas de Exceção

### `agenda_excecao`

Para datas específicas que sobrescrevem a disponibilidade recorrente (ex: mudou o horário de trabalho em um dia específico, ou fechou para um evento).

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | ID da exceção. |
| **profissional_id**| `INT` | `NOT NULL`, `UNIQUE(profissional_id, data)`, `FOREIGN KEY` | Profissional. |
| **data** | `DATE` | `NOT NULL` | Data específica da exceção. |
| **hora_inicio** | `TIME` | `DEFAULT NULL` | Novo horário de início (se não estiver fechado). |
| **hora_fim** | `TIME` | `DEFAULT NULL` | Novo horário de término (se não estiver fechado). |
| **fechado** | `BOOLEAN` | `DEFAULT 0` | 1 se o dia estiver totalmente indisponível. |
| **descricao** | `VARCHAR(255)` | `DEFAULT NULL` | Motivo da exceção. |

### `excecoes_recorrentes`

Para regras de indisponibilidade que se repetem (ex: folga fixa no primeiro sábado do mês).

| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | ID da exceção. |
| **profissional_id**| `INT` | `NOT NULL`, `FOREIGN KEY` | Profissional. |
| **descricao** | `VARCHAR(255)` | `DEFAULT NULL` | Descrição da regra. |
| **hora_inicio** | `TIME` | `NOT NULL` | Início da indisponibilidade. |
| **hora_fim** | `TIME` | `NOT NULL` | Fim da indisponibilidade. |