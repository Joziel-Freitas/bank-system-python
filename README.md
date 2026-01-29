# 🏦 PyBank System - CLI Banking Application

Aplicação bancária via linha de comando desenvolvida com foco em **Arquitetura de Software**, **Persistência de Dados** e **Segurança**.

## 📖 Sobre o Projeto

Este projeto foi desenvolvido como parte do meu portfólio de transição de carreira para Desenvolvimento Backend. O objetivo foi criar um sistema que fugisse de scripts simples e apresentasse uma arquitetura organizada, modular e escalável, sem depender de frameworks externos.

Nesta versão **2.0**, o sistema evoluiu de uma execução em memória para uma aplicação robusta com persistência de dados e tratamentos avançados de segurança e UX.

O foco central é demonstrar domínio sobre a linguagem Python e conceitos fundamentais de desenvolvimento, como:

* **Persistência de Dados:** Implementação manual de serialização JSON utilizando o padrão *Repository*.
* **Segurança Ofensiva/Defensiva:** Proteção contra enumeração de contas e acesso cruzado (*Cross-Access*).
* **Fail-Fast & UX:** Fluxos otimizados que validam o estado da conta antes de solicitar interações do usuário.
* **Gestão de Estado:** Controle lógico de sessões e prevenção de *crashes* em tempo de execução.

## 🏗️ Estrutura e Arquitetura

O sistema segue princípios de **Clean Architecture**, separando responsabilidades entre Domínio, Aplicação e Infraestrutura.

### Organização de Pastas

```text
BankSystem/
├── app/                # Camada de Aplicação
│   └── controllers.py  # Orquestração de fluxo e regras de aplicação (Fail-Fast)
├── data/               # [NOVO] Persistência de dados (Arquivos .json)
├── domain/             # Camada de Domínio (Core do Negócio)
│   ├── bank.py         # Regras de negócio, segurança e validação de sessão
│   ├── account.py      # Entidades de conta (Dataclasses)
│   └── person.py       # Entidades de Cliente
├── infra/              # Camada de Infraestrutura
│   ├── config.py       # Configurações gerais
│   ├── repository.py   # [NOVO] Implementação do Repository Pattern (Leitura/Escrita)
│   ├── io_utils.py     # Utilitários de I/O
│   └── views.py        # Interface com o usuário (CLI)
├── shared/             # Recursos Compartilhados
│   ├── exceptions.py   # Exceções personalizadas
│   └── validators.py   # Validadores de dados
└── main.py             # Entrypoint e ciclo de vida da aplicação
```

## 🛠️ Destaques Técnicos
1. Persistência e Serialização (JSON)
O sistema não perde dados ao ser fechado. Foi implementada uma camada de persistência (infra/repository.py) que serializa o estado complexo do banco (Contas, Clientes e Relacionamentos) para arquivos JSON, garantindo a continuidade das operações entre sessões.

2. Python Moderno e Dataclasses
Substituição de estruturas rígidas por Dataclasses, facilitando a tipagem, a mutabilidade controlada e a serialização dos objetos de domínio. Uso extensivo de Type Hints (Python 3.12+).

3. Segurança e Tratamento de Erros
Prevenção de Enumeração: O sistema trata tentativas de acesso cruzado (senha correta em conta errada) como "Conta não encontrada", impedindo que atacantes mapeiem credenciais válidas.

Blindagem de Sessão: O loop principal captura falhas críticas de integridade (RuntimeError), realizando o logout seguro do usuário em vez de derrubar a aplicação.

4. Design Patterns e UX
Repository Pattern: Abstração da camada de salvamento de dados.

Fail-Fast Strategy: Nos controladores, o sistema verifica o status da conta (Bloqueada/Ativa) antes de solicitar a senha ao usuário, evitando frustração e interações desnecessárias.

Strategy & State: Para validações e gestão de sessão (Logado/Convidado).

## 🚀 Como Executar
Pré-requisitos: Python 3.12 ou superior.

Clone o repositório:

git clone https://github.com/Joziel-Freitas/bank-system-python.git

Entre na pasta do projeto:

cd bank-system-python

Execute a aplicação (Nenhuma dependência externa necessária):

python main.py

Nota: A pasta data/ será criada automaticamente na primeira execução para salvar seus dados.

## 💻 Funcionalidades
O sistema simula um terminal bancário completo:

Autenticação: Login seguro via Token e Senha.

Operações Financeiras: Saque e Depósito (com persistência automática).

Gestão de Conta: Visualização de Saldo e Extrato.

Segurança: Bloqueio automático após 3 tentativas falhas de senha.

Recuperação: Fluxo de desbloqueio de conta (Unfreeze) com validação de dados pessoais (KBA - Knowledge Based Authentication).

Autor: Joziel Freitas Projeto desenvolvido com foco em Backend Engineering, Clean Code e Segurança.
