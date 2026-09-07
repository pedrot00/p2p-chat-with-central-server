import threading as th
import time

current_peer = None         # Var global para armazenar a conexao P2P ativa (se houver)

## BLOCO FUNCOES ---------------

def keep_alive(socket_client):              # Func p manter canal aberto (timeout 5sec)
    try:
        while True:
            msg = 'KEEP\r\n'
            socket_client.send(msg.encode('utf-8'))
            time.sleep(5)
    except Exception as e:
        print(f'<Error keep-alive>: {e}')
        return


def p2p_listen(socket_p2p):             # Func p aceitar conexao P2P e iniciar threads de handle
    global current_peer

    try:
        while True:
            conn, addr = socket_p2p.accept()
            data = conn.recv(2048).decode('utf-8')

            if data.startswith('USER'):
                peer_name = data.replace("USER ", "").strip()

                # SE JÁ ESTIVER OCUPADO → RECUSA
                if current_peer is not None:
                    try:
                        conn.send('BUSY\r\n'.encode('utf-8'))
                        conn.close()
                        print(f'<Tentativa de conexão recusada de {peer_name} - ocupado>\n')
                    except:
                        pass
                    continue

                # ACEITA
                print(f'\n<Nova conexão de: {peer_name}>\r\n')
                current_peer = conn
                init_thread_p2p_handle(conn, peer_name)

            else:
                conn.close()

    except Exception as e:
        print(f'<Error in P2P listen>: {e}\r\n')
        return


def handle_p2p_connection(conn, peer_name):                 # Func p lidar com msgs recebidas da conexao P2P (thread dedicada)
    global current_peer

    print(f'<Chat iniciado com {peer_name}>\r\n')

    while True:
        try:
            data = conn.recv(2048)

            if not data:
                print(f'<O usuário {peer_name} encerrou a conexão>\r\n')
                break

            msg = data.decode('utf-8')

            if msg.strip() == '/bye':
                print(f'<Conexão com {peer_name} finalizada. >\r\n')
                break

            print(f'{peer_name} diz: {msg.strip()}')

        except Exception as e:
            print(f'<Error na conexao {peer_name}>\r\n')
            break

    conn.close()
    current_peer = None


## BLOCO THREADS -----------------

def init_thread_keep(socket_client):                 # Func p iniciar thread de keep-alive (manter canal aberto)
    try:
        t_keep = th.Thread(target=keep_alive, args=(socket_client,))
        t_keep.daemon = True
        t_keep.start()
    except Exception as e:
        print(f'<Error initializing keep-alive thread>: {e}\r\n')


def init_thread_p2p_listen(socket_p2p):             # Func p iniciar thread de listen P2P (aceitar conexões P2P e iniciar threads de handle)
    try:
        t_p2p_listen = th.Thread(target=p2p_listen, args=(socket_p2p,))
        t_p2p_listen.daemon = True
        t_p2p_listen.start()
    except Exception as e:
        print(f'<Error initializing P2P listen thread>: {e}\r\n')


def init_thread_p2p_handle(conn, peer_name):       # Func p iniciar thread de handle P2P (lidar com msgs recebidas da conexao P2P)   
    try:
        t_p2p_handle = th.Thread(target=handle_p2p_connection, args=(conn, peer_name))
        t_p2p_handle.daemon = True
        t_p2p_handle.start()
    except Exception as e:
        print(f'<Error initializing P2P handle thread>: {e}\r\n')