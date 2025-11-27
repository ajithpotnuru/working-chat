import socket
import threading
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

def receive_loop(sock):
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                print("Disconnected from server.")
                break
            sys.stdout.write(data.decode('utf-8'))
            sys.stdout.flush()
    except Exception as e:
        print("Receive error:", e)
    finally:
        try:
            sock.close()
        except:
            pass
        sys.exit(0)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to Nexus Chat server at {SERVER_HOST}:{SERVER_PORT}")
    recv_thread = threading.Thread(target=receive_loop, args=(sock,), daemon=True)
    recv_thread.start()

    try:
        while True:
            line = input()
            if not line:
                continue
            sock.sendall((line + '\n').encode('utf-8'))
            if line.strip().lower() == '/quit':
                break
    except (KeyboardInterrupt, EOFError):
        try:
            sock.sendall(('/quit\n').encode('utf-8'))
        except:
            pass
    finally:
        sock.close()

if __name__ == '__main__':
    main()
