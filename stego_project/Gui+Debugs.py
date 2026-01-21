
from encrypt import build_bitstream, embed_bits
from decrypt import extract_bits, decode_message

import tkinter as tk
from tkinter import filedialog, messagebox


class StegoApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window
        self.title("Image Steganography Tool")
        self.geometry("1000x650")
        self.minsize(900, 600)

        # Colors
        self.bg_color = "#f4f6f8"
        self.sidebar_color = "#1f2933"
        self.accent_color = "#4f46e5"
        self.text_color = "#111827"

        self.configure(bg=self.bg_color)

        self.sidebar_visible = True
        self.build_layout()

    # ================= LAYOUT =================

    def build_layout(self):
        self.root_container = tk.Frame(self, bg=self.bg_color)
        self.root_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(
            self.root_container,
            bg=self.sidebar_color,
            width=220
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Separator
        tk.Frame(self.root_container, width=1, bg="#e5e7eb").pack(side="left", fill="y")

        # Main area
        self.main_area = tk.Frame(self.root_container, bg=self.bg_color)
        self.main_area.pack(side="left", fill="both", expand=True, padx=(20, 0))

        self.build_sidebar()
        self.build_topbar()
        self.build_pages()

    # ================= SIDEBAR =================

    def build_sidebar(self):
        tk.Label(
            self.sidebar,
            text="StegoTool",
            fg="white",
            bg=self.sidebar_color,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(25, 30))

        self.add_nav_button("Home", self.show_home)
        self.add_nav_button("Encrypt", self.show_encrypt)
        self.add_nav_button("Decrypt", self.show_decrypt)

    def add_nav_button(self, text, command):
        tk.Button(
            self.sidebar,
            text=text,
            command=command,
            bg=self.sidebar_color,
            fg="white",
            relief="flat",
            anchor="w",
            padx=20,
            pady=12,
            font=("Segoe UI", 12),
            cursor="hand2",
            activebackground="#374151"
        ).pack(fill="x", pady=6)

    # ================= TOP BAR =================

    def build_topbar(self):
        bar = tk.Frame(self.main_area, bg=self.bg_color, height=50)
        bar.pack(fill="x")

        tk.Button(
            bar,
            text="☰",
            bg=self.bg_color,
            fg=self.text_color,
            relief="flat",
            font=("Segoe UI", 16),
            command=self.toggle_sidebar
        ).pack(side="left", padx=20, pady=20)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side="left", fill="y")
        self.sidebar_visible = not self.sidebar_visible

    # ================= PAGES =================

    def build_pages(self):
        self.pages = {
            "Home": tk.Frame(self.main_area, bg=self.bg_color),
            "Encrypt": tk.Frame(self.main_area, bg=self.bg_color),
            "Decrypt": tk.Frame(self.main_area, bg=self.bg_color),
        }

        for p in self.pages.values():
            p.pack(fill="both", expand=True)

        self.build_home_page()
        self.build_encrypt_page()
        self.build_decrypt_page()
        self.show_home()

    # ================= HOME =================

    def build_home_page(self):
        page = self.pages["Home"]

        tk.Label(
            page,
            text="Image Steganography Tool",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI", 26, "bold")
        ).pack(pady=(120, 10))

        tk.Label(
            page,
            text="Secure message hiding using encryption",
            bg=self.bg_color,
            fg="#6b7280",
            font=("Segoe UI", 12)
        ).pack(pady=(0, 40))

        btns = tk.Frame(page, bg=self.bg_color)
        btns.pack()

        tk.Button(
            btns,
            text="Encrypt",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI", 14, "bold"),
            padx=40,
            pady=12,
            relief="flat",
            command=self.show_encrypt
        ).grid(row=0, column=0, padx=15)

        tk.Button(
            btns,
            text="Decrypt",
            bg="#374151",
            fg="white",
            font=("Segoe UI", 14),
            padx=40,
            pady=12,
            relief="flat",
            command=self.show_decrypt
        ).grid(row=0, column=1, padx=15)

    # ================= ENCRYPT =================

    def build_encrypt_page(self):
        page = self.pages["Encrypt"]

        card = self.card(page)

        # Image
        self.encrypt_image_path = tk.StringVar(value="No image selected")
        self.file_picker(card, self.encrypt_image_path, self.select_encrypt_image)

        self.section(card, "Message")
        self.encrypt_message = tk.Text(card, height=6, font=("Segoe UI", 11))
        self.encrypt_message.pack(fill="x")

        self.section(card, "Encryption Key")
        self.encrypt_key = tk.Entry(card, show="●")
        self.encrypt_key.pack(fill="x")

        self.section(card, "Channel Mode")
        self.encrypt_channel = tk.IntVar(value=3)
        self.channel_buttons(card, self.encrypt_channel)

        tk.Button(
            card,
            text="Encrypt",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI", 13, "bold"),
            padx=40,
            pady=12,
            relief="flat",
            command=self.run_encrypt
        ).pack(pady=25)

    # ================= DECRYPT =================

    def build_decrypt_page(self):
        page = self.pages["Decrypt"]

        card = self.card(page)

        self.decrypt_image_path = tk.StringVar(value="No image selected")
        self.file_picker(card, self.decrypt_image_path, self.select_decrypt_image)

        self.section(card, "Decryption Key")
        self.decrypt_key = tk.Entry(card, show="●")
        self.decrypt_key.pack(fill="x")

        self.section(card, "Channel Mode")
        self.decrypt_channel = tk.IntVar(value=3)
        self.channel_buttons(card, self.decrypt_channel)

        tk.Button(
            card,
            text="Decrypt",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI", 13, "bold"),
            padx=40,
            pady=12,
            relief="flat",
            command=self.run_decrypt
        ).pack(pady=25)

    # ================= UI HELPERS =================

    def card(self, parent):
        c = tk.Frame(
            parent,
            bg="white",
            highlightthickness=1,
            highlightbackground="#e5e7eb"
        )
        c.pack(fill="both", expand=True, padx=40, pady=30)
        c.configure(padx=30, pady=25)
        return c

    def section(self, parent, text):
        tk.Label(
            parent,
            text=text,
            bg="white",
            fg=self.text_color,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(15, 5))

    def file_picker(self, parent, var, command):
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=(0, 20))

        tk.Button(
            row,
            text="Select Image",
            bg=self.accent_color,
            fg="white",
            padx=20,
            pady=8,
            relief="flat",
            command=command
        ).pack(side="left")

        tk.Label(
            row,
            textvariable=var,
            bg="white",
            fg="#374151"
        ).pack(side="left", padx=15)

    def channel_buttons(self, parent, var):
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=10)

        def set_mode(m):
            var.set(m)
            b1.config(bg=self.accent_color if m == 1 else "#e5e7eb",
                      fg="white" if m == 1 else self.text_color)
            b3.config(bg=self.accent_color if m == 3 else "#e5e7eb",
                      fg="white" if m == 3 else self.text_color)

        b1 = tk.Button(row, text="1-Channel", padx=30, pady=10, relief="flat",
                       command=lambda: set_mode(1))
        b1.pack(side="left", padx=10)

        b3 = tk.Button(row, text="3-Channel", padx=30, pady=10, relief="flat",
                       bg=self.accent_color, fg="white",
                       command=lambda: set_mode(3))
        b3.pack(side="left", padx=10)

    # ================= LOGIC =================

    def select_encrypt_image(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if p:
            self.encrypt_image_path.set(p)

    def select_decrypt_image(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if p:
            self.decrypt_image_path.set(p)

    def run_encrypt(self):
        try:
            img = self.encrypt_image_path.get()
            msg = self.encrypt_message.get("1.0", "end").strip()
            key = self.encrypt_key.get()
            mode = self.encrypt_channel.get()

            if "No image" in img or not msg or not key:
                raise ValueError("All fields are required")

            out = filedialog.asksaveasfilename(defaultextension=".png")
            if not out:
                return

            embed_bits(img, build_bitstream(msg, key, mode), mode, out)
            messagebox.showinfo("Success", "Message encrypted successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_decrypt(self):
        try:
            img = self.decrypt_image_path.get()
            key = self.decrypt_key.get()

            bits = extract_bits(img, 3)
            msg, actual = decode_message(bits, key)

            messagebox.showinfo("Decrypted Message", msg)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= NAV =================

    def show_home(self):
        self.show_page("Home")

    def show_encrypt(self):
        self.show_page("Encrypt")

    def show_decrypt(self):
        self.show_page("Decrypt")

    def show_page(self, name):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[name].pack(fill="both", expand=True)


if __name__ == "__main__":
    StegoApp().mainloop()
