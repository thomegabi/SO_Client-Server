import socket
import threading
import os
import subprocess
import json
import platform
import pyautogui
import time

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
                path = json_message['command'] if json_message['command'] else server_directory
                try:
                    files = os.listdir(path)
                    client_socket.send((json.dumps(files) + '\n').encode('utf-8'))
                except FileNotFoundError:
                    client_socket.send((json.dumps([]) + '\n').encode('utf-8'))
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
    except Exception as e:
        print(f"Exceção inesperada no cliente {client_address}: {e}")
    finally:
        print(f"Conexão com o cliente {client_address} fechada.")
        clients.remove((client_socket, client_address))
        client_socket.close()

def perform_mouse_action(command, params):
    print(f"Entrando no perform com o comando: {command}")
    try:
        command = command.split(':')[0].strip()
        if command.strip() == 'limit':
            print(f"Entrando no limit")
            limit_mouse_movement(params.get('left', 0), params.get('top', 0), params.get('right', 0), params.get('bottom', 0), params.get('duration', 5))
        elif command.strip() == 'lock':
            lock_mouse_movement()
        else:
            print(f"Comando desconhecido: {command}")
    except Exception as e:
        print(f"Erro ao processar ação do mouse: {e}")

import pyautogui

def limit_mouse_movement(around_size):
    try:
        current_x, current_y = pyautogui.position()
        left = current_x - around_size
        top = current_y - around_size
        right = current_x + around_size
        bottom = current_y + around_size

        while True:
            new_x, new_y = pyautogui.position()
            if not (left <= new_x <= right and top <= new_y <= bottom):
                pyautogui.moveTo(
                    min(max(left, new_x), right), 
                    min(max(top, new_y), bottom)
                )
    except Exception as e:
        print(f"Erro ao limitar o movimento do mouse: {e}")


def lock_mouse_movement():
    print(f"Entrou")
    start_time = time.time()
    x, y = pyautogui.position()
    print(f"Travando o mouse na posição ({x}, {y}) por 5 segundos")

    def lock_movement():
        while time.time() - start_time < 5:
            pyautogui.moveTo(x, y)
            time.sleep(0.01)
        print("Destravando o mouse")

    threading.Thread(target=lock_movement).start()

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
