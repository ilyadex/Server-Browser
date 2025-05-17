import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import urllib.request

CONFIG_FILE = "servers.cfg"

def load_config_path():
    if not os.path.exists(CONFIG_FILE):
        messagebox.showerror("Ошибка", f"Файл {CONFIG_FILE} не найден.")
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def load_servers(path):
    try:
        if path.startswith("http://") or path.startswith("https://"):
            with urllib.request.urlopen(path) as url:
                return json.load(url)
        else:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        messagebox.showerror("Ошибка загрузки", str(e))
        return {}

class ServerBrowser(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Server Browser")
        self.geometry("820x550")
        self.configure(bg="#2d2d2d")

        self.servers = {}
        self.filtered = {}

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        tk.Label(self, text="Поиск по MOTD:", bg="#2d2d2d", fg="white").pack(pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.update_list())
        tk.Entry(self, textvariable=self.search_var, width=50).pack(pady=5)

        columns = ("IP", "Version", "Players", "MOTD")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180 if col != "MOTD" else 300)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.copy_button = tk.Button(self, text="Скопировать IP", command=self.copy_selected_ip)
        self.copy_button.pack(pady=5)

    def load_data(self):
        path = load_config_path()
        if not path:
            return
        self.servers = load_servers(path)
        self.update_list()

    def update_list(self):
        query = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for ip, info in self.servers.items():
            motd = str(info.get("motd", ""))
            if query in motd.lower():
                self.tree.insert("", "end", values=(
                    ip,
                    info.get("version", "?"),
                    info.get("players", "?"),
                    motd
                ))

    def copy_selected_ip(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Выбор", "Выберите сервер для копирования IP.")
            return
        ip = self.tree.item(selected[0])["values"][0]
        self.clipboard_clear()
        self.clipboard_append(ip)
        self.update()
        messagebox.showinfo("Скопировано", f"IP-адрес {ip} скопирован.")

if __name__ == "__main__":
    app = ServerBrowser()
    app.mainloop()
