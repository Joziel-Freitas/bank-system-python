# 🏦 PyBank System - Enterprise Architecture

> Um sistema bancário CLI robusto, demonstrando aplicação prática de **Clean Architecture**, **DDD**, **Segurança Defensiva** e **Python Moderno**.

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-complete-success)

## 📖 Sobre o Projeto

Este não é apenas um simulador de conta bancária. É um estudo de caso avançado sobre como estruturar aplicações Python complexas sem depender de frameworks pesados.

O projeto resolve problemas reais de engenharia de software, como:
- **Gestão de Estado:** Controle estrito de sessões de usuário e hardware simulado (cartões).
- **Segurança:** Proteção contra *Enumeration Attacks*, *Zombie Sessions* e validação *Fail-Fast*.
- **Desacoplamento:** Uso de Injeção de Dependência e separação clara entre I/O, Lógica de Negócio e Orquestração.

## 🏗️ Arquitetura e Design Patterns

O sistema segue princípios de **Domain-Driven Design (DDD)**, onde o núcleo do negócio (`domain`) não conhece o mundo externo.

### Estrutura de Pastas
```text
BankSystem/
├── app/                # Camada de Aplicação (Controllers & Orchestration)
│   └── controllers.py  # Controladores Genéricos e Máquinas de Estado
├── domain/             # Camada de Domínio (Enterprise Business Rules)
│   ├── bank.py         # Aggregate Root & Factory de Sessões
│   ├── account.py      # Template Method para Contas (Checking/Savings)
│   └── person.py       # Entidades e Value Objects (AccountCard)
├── infra/              # Camada de Infraestrutura (I/O & Config)
│   ├── config.py       # Configuration as Code (TypedDicts)
│   └── io_utils.py     # Motor de I/O Agnóstico e Loops de Retry
├── shared/             # Kernel Compartilhado
│   ├── exceptions.py   # Taxonomia de Erros Hierárquica
│   └── types.py        # Enums Semânticos e Contextos
└── main.py             # Composition Root & Entrypoint

Patterns Implementados
Generic Controllers: Uso de TypeVar e Generic[T] para criar controladores de criação (CreationController) que funcionam para qualquer entidade.

Strategy Pattern: Utilizado na seleção de algoritmos de validação e nos fluxos de operação (Saque, Depósito, Extrato).

State Pattern: Gestão do ciclo de vida da sessão (Logged In, Logged Out, Card Inserted).

Aggregate Root: A classe Bank garante a consistência de todas as operações entre Clientes e Contas.

Fail Fast & Exception Mapping: Um sistema sofisticado que traduz exceções técnicas (ex: ValueError) em contextos de negócio (ex: BankContext.PASSWORD), permitindo que a UI solicite correções específicas ao usuário.

🛡️ Destaques de Segurança
Anti-Enumeration: O login falha de forma genérica ou silenciosa em casos específicos para impedir que atacantes descubram quais CPFs estão cadastrados.

Token-Based Access: O sistema utiliza AuthToken imutável. Os controladores não acessam contas diretamente, eles trocam tokens por acesso a cada operação.

Zombie Session Prevention: O controlador principal garante a destruição do token e a ejeção do "cartão" da memória em caso de erros críticos ou logout forçado.

Input Sanitization: Camada de verify.py e validators.py garante que dados sujos nunca cheguem às entidades de domínio.

🚀 Como Executar
Pré-requisitos
Python 3.12 ou superior.

Passo a Passo
Clone o repositório:

Bash

git clone [https://github.com/Joziel-Freitas/bank-system-python.git](https://github.com/Joziel-Freitas/bank-system-python.git)
cd bank-system-python
Execute a aplicação (nenhuma instalação de biblioteca externa necessária):

Bash

python main.py
💻 Exemplo de Uso
O sistema simula um terminal de autoatendimento:

Escolha o Banco: Selecione entre as opções de bancos disponíveis (cada um com seu código de agência).

Identificação: Faça login com Cartão Virtual (selecionando da lista) ou Digitação Manual.

Operações: Realize saques (com lógica de Cheque Especial), depósitos e visualize extratos.

Admin: Desbloqueie contas congeladas respondendo a desafios de segurança (KBA - Knowledge Based Authentication).

Autor: Joziel Freitas Projeto desenvolvido com foco em Excelência Técnica e Arquitetura de Software.
