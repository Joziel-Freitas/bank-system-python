# 🏦 PyBank System - CLI Banking Application

> Aplicação bancária via linha de comando desenvolvida com foco em **Lógica de Programação**, **Estrutura de Dados** e **Boas Práticas de Engenharia de Software**.

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-portfolio-orange)

## 📖 Sobre o Projeto

Este projeto foi desenvolvido como parte do meu portfólio de transição de carreira para Desenvolvimento Backend. O objetivo foi criar um sistema que fugisse de scripts simples e apresentasse uma arquitetura organizada, modular e escalável, sem depender de frameworks externos.

O foco central é demonstrar domínio sobre a linguagem Python e conceitos fundamentais de desenvolvimento, como:
- **Separação de Responsabilidades:** Divisão clara entre interface (CLI), regras de negócio e orquestração.
- **Tratamento de Erros:** Fluxos robustos que impedem o fechamento abrupto do programa (`crashes`).
- **Gestão de Estado:** Controle lógico de sessões de usuário (Logado/Deslogado).

## 🏗️ Estrutura e Arquitetura

O sistema foi estruturado em camadas lógicas para garantir desacoplamento e facilidade de manutenção.

### Organização de Pastas
```text
BankSystem/
├── app/                # Camada de Aplicação
│   └── controllers.py  # Controladores responsáveis pelo fluxo das operações
├── domain/             # Camada de Domínio (Core do Negócio)
│   ├── bank.py         # Gerenciamento central das contas e sessões
│   ├── account.py      # Lógica das contas (Corrente/Poupança)
│   └── person.py       # Modelos de Cliente e Cartão
├── infra/              # Camada de Infraestrutura e Interface
│   ├── config.py       # Configurações gerais
│   ├── io_utils.py     # Utilitários de entrada e saída (Input/Output)
│   ├── verify.py       # Verificações de baixo nível (Tipagem e Dados)
│   └── views.py        # Telas e Menus do terminal
├── shared/             # Recursos Compartilhados
│   ├── exceptions.py   # Exceções personalizadas do sistema
│   ├── types.py        # Enums e Definições de Tipos
│   └── validators.py   # Validadores de dados (ex: formato de CPF)
└── main.py             # Ponto de entrada da aplicação

🛠️ Destaques Técnicos
Python Moderno e Tipagem
Uso extensivo de Type Hints e recursos do Python 3.12+ para garantir um código mais seguro e legível.

Uso de Generic[T] e TypeVar para criar controladores reutilizáveis.

Aplicação de match/case para controle de fluxo mais limpo.

Design Patterns Aplicados
Conceitos de orientação a objetos aplicados de forma prática:

Strategy: Utilizado para definir diferentes comportamentos de validação e operações.

State: Gerenciamento do estado da sessão do usuário (ex: impedir saques se não estiver logado).

Template Method: Estrutura base para diferentes tipos de contas bancárias.

Robustez e Validação (Fail-Fast)
O sistema implementa uma camada de validação (validators.py e verify.py) que garante
que dados incorretos sejam barrados antes de serem processados pelas regras de negócio.
Erros técnicos são capturados e traduzidos em mensagens amigáveis para o usuário.

🚀 Como Executar
Pré-requisitos: Python 3.12 ou superior.

Clone o repositório:
git clone https://github.com/Joziel-Freitas/bank-system-python.git

Entre na pasta do projeto:
cd bank-system-python

Execute a aplicação (não requer instalação de bibliotecas externas):
python main.py

💻 Funcionalidades
O sistema simula um terminal de autoatendimento com as seguintes opções:

Autenticação: Login via seleção de cartão virtual ou digitação manual.

Transações: Saque (com lógica de cheque especial), Depósito e Transferências.

Consultas: Visualização de saldo e extrato detalhado.

Admin: Funcionalidades de desbloqueio de conta mediante validação de segurança.

Autor: Joziel Freitas
Projeto desenvolvido com foco em Clean Code e Lógica de Programação.
