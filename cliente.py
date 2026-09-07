# INF450 - Redes de Computadores - TP1/2026
# Pedro Santos Teixeira - 116224

import socket
import p2p_utils
from p2p_utils import init_thread_keep, init_thread_p2p_listen, init_thread_p2p_handle

HOST = '200.235.131.66'  
PORT = 10000
dest = (HOST, PORT)

# 1. SOCKET PARA ESCUTA P2P (lado Servidor para os amigos)
socket_p2p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_p2p.bind(('', 0))
socket_p2p.listen()

CLIENT_PORT = socket_p2p.getsockname()[1]

# 2. SOCKET CLIENTE-SERVIDOR (canal com o servidor central)
user_name = input('Nome de usuário: ')

socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.connect(dest)

msg = f'USER {user_name}:{CLIENT_PORT}\r\n'         # Primeira msg enviada ao servidor central: USER <nome>:<porta P2P>
socket_client.send(msg.encode('utf-8'))

init_thread_keep(socket_client)         # Inicia thread de keep-alive (manter canal aberto)
init_thread_p2p_listen(socket_p2p)      # Inicia thread de listen P2P (aceitar conexões P2P -> iniciar threads de handle)

## BLOCO DECISOES ----------------

def decision_loop():                    # Loop principal de decisões do cliente (comandos /list, /chat, /bye, /exit e envio de mensagens P2P)
    while True:
        prompt = "" if p2p_utils.current_peer else "Insira o comando (/list /chat /bye /exit): " 
        cmd = input(prompt)         # Prompt diferente se n estiver em chat ativo

        if cmd == '/list':
            try:
                socket_client.send('LIST\r\n'.encode('utf-8'))
                data = socket_client.recv(2048).decode('utf-8').strip()

                if data.startswith('LIST'):
                    users = data.replace('LIST ', '').split(':')
                    print("\nAtivos:")
                    for user in users:
                        print(f"- {user}")
                    print()
                else:
                    print("<Resposta inesperada do servidor>\n")

            except Exception as e:
                print(f"[Erro no LIST]: {e}\n")

        elif cmd.startswith('/chat'):
            try:
                parts = cmd.split()
                if len(parts) != 2:
                    print("<Uso correto: /chat <usuario>>\n")
                    continue

                target_user = parts[1]
                msg = f'ADDR {target_user}\r\n'
                socket_client.send(msg.encode('utf-8'))

                data = socket_client.recv(2048).decode('utf-8').strip()

                if data.startswith('ADDR'):
                    addr_info = data.replace('ADDR ', '').split(':')

                    if len(addr_info) != 3:
                        print("<Resposta de endereço mal formatada>\n")
                        continue

                    returned_name, target_ip, target_port = addr_info
                    target_port = int(target_port)

                    print(f"<Conectando a {target_user} em {target_ip}:{target_port}...>\n")

                    socket_p2p_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    try:
                        socket_p2p_peer.connect((target_ip, target_port))
                    except Exception as e:
                        print(f"<Erro ao conectar>: {e}\n")
                        continue

                    print(f"<Conectado a {target_user}>")

                    user_msg = f'USER {user_name}\r\n'
                    socket_p2p_peer.send(user_msg.encode('utf-8'))

                    p2p_utils.current_peer = socket_p2p_peer
                    init_thread_p2p_handle(socket_p2p_peer, target_user)

                else:
                    print(f"<Resposta inesperada do servidor]: {data}>\n")

            except Exception as e:
                print(f"<Erro no /chat>: {e}\n")

        elif cmd == '/bye':
            if p2p_utils.current_peer:
                try:
                    p2p_utils.current_peer.send('/bye\r\n'.encode('utf-8'))
                    try:
                        p2p_utils.current_peer.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    p2p_utils.current_peer.close()
                    p2p_utils.current_peer = None
                    print(f"<Conexão P2P encerrada>\n")
                except Exception as e:
                    print(f"<Erro ao encerrar conexão P2P>: {e}\n")
            else:
                print("<Nenhuma conexão P2P ativa para encerrar>\n")

        elif cmd == '/exit':
            print("<Encerrando cliente...>\n")
            try:
                if p2p_utils.current_peer:
                    p2p_utils.current_peer.send('/bye\r\n'.encode('utf-8'))
                    try:
                        p2p_utils.current_peer.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    p2p_utils.current_peer.close()

                socket_client.close()
                socket_p2p.close()
            except Exception as e:
                print(f"<Erro ao fechar conexões>: {e}\n")
            break

        else:
            if p2p_utils.current_peer:
                try:
                    msg = cmd + '\r\n'
                    p2p_utils.current_peer.send(msg.encode('utf-8'))
                except Exception as e:
                    print(f"<Erro ao enviar mensagem>: {e}\n")
            else:
                print("<Nenhuma conexão P2P ativa>\n")

decision_loop()     # Inicia again o loop de decisoes do cliente (comandos /list, /chat, /bye, /exit e envio de mensagens P2P)