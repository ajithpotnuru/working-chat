import socket
import threading
import traceback

HOST = '0.0.0.0'   
PORT = 5000        

clients_lock = threading.Lock()
clients = {}  # socket -> {'name': str, 'addr': (ip,port)}

def send(sock, msg):
    try:
        sock.sendall((msg + '\n').encode('utf-8'))
    except Exception:
        remove_client(sock)

def broadcast(sender_sock, msg):
    with clients_lock:
        for sock in list(clients.keys()):
            if sock is not sender_sock:
                send(sock, msg)

def list_users():
    with clients_lock:
        return [info['name'] for info in clients.values()]

def find_sock_by_name(name):
    with clients_lock:
        for sock, info in clients.items():
            if info['name'] == name:
                return sock
    return None

def remove_client(sock):
    with clients_lock:
        info = clients.pop(sock, None)
    if info:
        msg = f"*** {info['name']} has left the chat."
        print(msg)
        broadcast(None, msg)
    try:
        sock.close()
    except Exception:
        pass

def client_thread(sock, addr):
    try:
        send(sock, "Welcome to Nexus Chat!  /name <Shiva>")
        with clients_lock:
            clients[sock] = {'name': f"{addr[0]}:{addr[1]}", 'addr': addr}
        broadcast(sock, f"*** {clients[sock]['name']} has joined the chat.")
        while True:
            data = sock.recv(4096)
            if not data:
                break
            text = data.decode('utf-8').strip()
            if not text:
                continue

            # Commands
            if text.startswith('/'):
                parts = text.split(' ', 2)
                cmd = parts[0].lower()

                if cmd == '/name':
                    if len(parts) < 2 or not parts[1].strip():
                        send(sock, "Usage: /name <Shiva>")
                        continue
                    newname = parts[1].strip()
                    with clients_lock:
                        oldname = clients[sock]['name']
                        clients[sock]['name'] = newname
                    broadcast(None, f"*** {oldname} is now known as {newname}")
                    send(sock, f"Name changed to {newname}")

                elif cmd == '/list':
                    users = list_users()
                    send(sock, "Connected users: " + ", ".join(users))

                elif cmd == '/pm':
                    if len(parts) < 3:
                        send(sock, "Usage: /pm <user> <message>")
                        continue
                    target, message = parts[1], parts[2]
                    target_sock = find_sock_by_name(target)
                    if not target_sock:
                        send(sock, f"User '{target}' not found.")
                        continue
                    sender_name = clients[sock]['name']
                    send(target_sock, f"[PM] {sender_name}: {message}")
                    send(sock, f"[PM -> {target}] {message}")

                elif cmd == '/quit':
                    send(sock, "Goodbye!")
                    break

                else:
                    send(sock, f"Unknown command: {cmd}")

            else:
                sender_name = clients[sock]['name']
                message = f"{sender_name}: {text}"
                print(message)
                broadcast(sock, message)
                send(sock, f"You: {text}")  # echo back to sender

    except Exception as e:
        print("Exception in client thread:", e)
        traceback.print_exc()
    finally:
        remove_client(sock)

def main():
    print(f"Starting Nexus Chat server on {HOST}:{PORT}")
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(100)
    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            print(f"Accepted connection from {client_addr}")
            t = threading.Thread(target=client_thread, args=(client_sock, client_addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        server_sock.close()
        with clients_lock:
            for sock in list(clients.keys()):
                try:
                    sock.close()
                except Exception:
                    pass

if __name__ == '__main__':
    main()

