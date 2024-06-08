import socket
import json
import os
import time

def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 9999))
        s.sendall(json.dumps(command).encode('utf-8'))
        response = s.recv(4096).decode('utf-8')
        return response

def test_execute_command():
    command = {
        'action': 'execute',
        'command': 'echo Hello, World!'
    }
    response = send_command(command)
    assert response.strip() == 'Hello, World!', f"Expected 'Hello, World!', got {response}"

current_directory = os.path.dirname(os.path.abspath(__file__))

server_directory = os.path.join(current_directory, '..', 'servidor')

def test_list_dir():
    command = {
        'action': 'list_dir',
        'path': server_directory
    }
    response = send_command(command)
    files = json.loads(response)
    assert isinstance(files, list), "Expected a list of files"
    assert 'server.py' in files, f"'server.py' not found in {files}"


def test_sys_info():
    command = {
        'action': 'sys_info'
    }
    response = send_command(command)
    info = json.loads(response)
    assert 'os' in info, "Expected 'os' in system info"
    assert 'platform' in info, "Expected 'platform' in system info"
    assert 'cwd' in info, "Expected 'cwd' in system info"

def test_mouse_control():
    command = {
        'action': 'mouse_control',
        'command': 'move',
        'params': {'x': 100, 'y': 100}
    }
    response = send_command(command)
    assert response == '', f"Expected no response, got {response}"


def dramatic_pause():
    print("Testing", end="", flush=True)
    for _ in range(2):
        time.sleep(1)
        print(".", end="", flush=True)
    print()

if __name__ == "__main__":
    test_execute_command()
    print("test_execute_command passed")
    
    dramatic_pause()  
    
    test_list_dir()
    print("test_list_dir passed")
    
    dramatic_pause()  
    
    test_sys_info()
    print("test_sys_info passed")
    
    dramatic_pause()  
    
    test_mouse_control()
    print("test_mouse_control passed")
    
    print("All tests passed")

