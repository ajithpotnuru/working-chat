import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("Nexus Chat")

        self.txt_area = scrolledtext.ScrolledText(master, state='disabled', wrap=tk.WORD, width=60, height=20)
        self.txt_area.pack(padx=10, pady=8)

        self.entry = tk.Entry(master, width=50)
        self.entry.pack(side=tk.LEFT, padx=(10,0), pady=(0,10))
        self.entry.bind('<Return>', self.send_message)

        self.send_btn = tk.Button(master, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((SERVER_HOST, SERVER_PORT))
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Could not connect to server: {e}")
            master.destroy()
            return

        self.running = True
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def append(self, text):
        self.txt_area.configure(state='normal')
        self.txt_area.insert(tk.END, text + '\n')
        self.txt_area.configure(state='disabled')
        self.txt_area.yview(tk.END)

    def receive_loop(self):
        try:
            while self.running:
                data = self.sock.recv(4096)
                if not data:
                    self.append("Disconnected from server.")
                    break
                for line in data.decode('utf-8').splitlines():
                    self.append(line)
        except Exception as e:
            self.append(f"Receive error: {e}")
        finally:
            self.sock.close()

    def send_message(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        try:
            self.sock.sendall((text + '\n').encode('utf-8'))
        except Exception as e:
            self.append(f"Send failed: {e}")
            return
        self.entry.delete(0, tk.END)
        if text.lower() == '/quit':
            self.running = False
            self.master.after(100, self.master.destroy)

def main():
    root = tk.Tk()
    app = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.sock.sendall(('/quit\n').encode('utf-8')) if app.sock else None, root.destroy()))
    root.mainloop()

if __name__ == '__main__':
    main()
