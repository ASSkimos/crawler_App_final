import asyncio
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logic

visited_urls = set()  # Множество для хранения уже посещенных URL


class CrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Crawler")

        # URL input
        ttk.Label(root, text="Введите URL:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Depth input
        ttk.Label(root, text="Глубина:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.depth_entry = ttk.Entry(root, width=10)
        self.depth_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Output display
        self.output = tk.Text(root, wrap=tk.WORD, width=80, height=20)
        self.output.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # Choose directory button
        self.directory_button = ttk.Button(root, text="Выбрать папку для сохранения", command=self.choose_directory)
        self.directory_button.grid(row=3, column=0, padx=5, pady=5)

        # Start crawling button
        self.crawl_button = ttk.Button(root, text="Начать краулинг", command=self.start_crawl)
        self.crawl_button.grid(row=3, column=1, padx=5, pady=5)

        # Save directory path
        self.save_directory = ""

    def choose_directory(self):
        self.save_directory = filedialog.askdirectory()
        if self.save_directory:
            self.output.insert(tk.END, f"Выбранная папка: {self.save_directory}\n")
        else:
            self.output.insert(tk.END, "Папка для сохранения не выбрана.\n")

    def start_crawl(self):
        url = self.url_entry.get()
        depth = self.depth_entry.get()

        if not url or not depth:
            messagebox.showerror("Ошибка", "Пожалуйста, введите URL и глубину.")
            return

        if not self.save_directory:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите папку для сохранения.")
            return

        try:
            depth = int(depth)
        except ValueError:
            messagebox.showerror("Ошибка", "Глубина должна быть числом.")
            return

        self.output.insert(tk.END, "Начало краулинга...\n")
        asyncio.run(logic.main(url, depth, self.output, self.save_directory))


if __name__ == "__main__":
    root = tk.Tk()
    app = CrawlerApp(root)
    root.mainloop()
