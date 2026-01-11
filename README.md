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
