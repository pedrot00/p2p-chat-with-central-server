# 📡 - p2p-chat-com-servidor-central

**Sistema de chat peer-to-peer com servidor central para descoberta de usuários e suporte a NAT traversal.**

---

## 📌 Visão Geral

Este projeto implementa um **sistema de chat descentralizado P2P** utilizando uma arquitetura híbrida:

- Um **servidor central** gerencia o registro de usuários, mantém a lista de ativos e fornece os endereços dos pares.
- **Conexões P2P diretas** entre os clientes permitem mensagens privadas e independentes do servidor.

O sistema foi desenvolvido para a disciplina **INF450 - Redes de Computadores**.

---


### Componentes Principais

| Componente | Descrição |
|-----------|-----------|
| **Servidor Central** | Gerencia cadastro de usuários, responde a `/list` e `/chat`, fornece endereços dos pares |
| **Socket P2P** | Cada cliente abre uma porta de escuta para conexões P2P recebidas |
| **Thread Keep-Alive** | Mantém a conexão com o servidor via mensagens `KEEP` periódicas |
| **Thread P2P Handler** | Gerencia a sessão de chat ativa, recebe e envia mensagens diretamente entre pares |

---

## 🚀 Funcionalidades

- ✅ **Registro de usuário** – cada cliente se registra com um nome único e porta P2P
- ✅ **Lista de usuários ativos** – comando `/list` retorna todos os usuários online
- ✅ **Chat P2P direto** – comando `/chat <usuário>` estabelece conexão TCP direta entre pares
- ✅ **Sessões concorrentes** – gerencia múltiplas tentativas de conexão com rejeição por ocupado
- ✅ **Desconexão graciosa** – `/bye` encerra a sessão P2P, `/exit` finaliza o cliente
- ✅ **Thread-safe** – utiliza threads daemon para operações concorrentes

---

## 📡 Protocolo

### Cliente ↔ Servidor

| Comando | Formato | Descrição |
|---------|---------|-----------|
| `USER` | `USER <nome>:<porta>` | Registra o usuário no servidor |
| `LIST` | `LIST` | Solicita lista de usuários ativos |
| `ADDR` | `ADDR <alvo>` | Solicita IP/porta do usuário alvo |
| `KEEP` | `KEEP` | Mensagem de keep-alive (a cada 5s) |

### Cliente ↔ Cliente (P2P)

| Comando | Formato | Descrição |
|---------|---------|-----------|
| `USER` | `USER <nome>` | Identifica o peer na conexão |
| `/bye` | `/bye` | Encerra a sessão P2P |
| `BUSY` | `BUSY` | Rejeita conexão se o peer estiver ocupado |
| `<texto>` | Qualquer outra mensagem | Mensagem de chat enviada diretamente |

## 🛠️ Tecnologias

- Python 3
- Socket Programming (TCP)
- Threading
- Protocolo customizado sobre TCP

---

## 🚀 Como Executar

### 1. Inicie o Servidor Central (se não estiver em execução)

```bash
python server.py   # (código do servidor não incluso, assumindo porta 10000)
