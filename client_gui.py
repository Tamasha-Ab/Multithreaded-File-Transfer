import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Client")

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
        self.text_area.grid(column=0, row=0, padx=10, pady=10)

        self.entry = tk.Entry(root, width=50)
        self.entry.grid(column=0, row=1, padx=10, pady=10)

        self.send_button = tk.Button(root, text="Send", command=self.send_command)
        self.send_button.grid(column=0, row=2, padx=10, pady=10)

        self.search_button = tk.Button(root, text="Search File", command=self.search_file)
        self.search_button.grid(column=0, row=3, padx=10, pady=10)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)

        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.start()

        self.selected_file_path = None

    def send_command(self):
        data = self.entry.get()
        self.entry.delete(0, tk.END)
        data = data.split(" ")
        cmd = data[0]

        if cmd == "HELP":
            self.client.send(cmd.encode(FORMAT))
        elif cmd == "LOGOUT":
            self.client.send(cmd.encode(FORMAT))
            self.client.close()
            self.root.quit()
        elif cmd == "LIST":
            self.client.send(cmd.encode(FORMAT))
        elif cmd == "DELETE":
            self.client.send(f"{cmd}@{data[1]}".encode(FORMAT))
        elif cmd == "UPLOAD":
            if self.selected_file_path:
                with open(self.selected_file_path, "rb") as f:
                    file_data = f.read()
                filename = os.path.basename(self.selected_file_path)
                send_data = f"{cmd}@{filename}@".encode(FORMAT) + file_data
                self.client.send(send_data)
                self.selected_file_path = None
            else:
                messagebox.showerror("Error", "No file selected or invalid file type")

    def search_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.selected_file_path = path
            self.entry.insert(0, f"UPLOAD {path}")
        else:
            messagebox.showerror("Error", "No file selected or invalid file type")

    def receive_data(self):
        while True:
            try:
                data = self.client.recv(SIZE).decode(FORMAT)
                cmd, msg = data.split("@")
                if cmd == "DISCONNECTED":
                    self.text_area.insert(tk.END, f"[SERVER]: {msg}\n")
                    break
                elif cmd == "OK":
                    self.text_area.insert(tk.END, f"{msg}\n")
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()