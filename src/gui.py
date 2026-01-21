from encrypt import build_bitstream, embed_bits
from decrypt import extract_bits, decode_message

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
import os


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color, fg_color, width=200, height=50, hover_color=None, text_font=("Segoe UI", 11, "bold")):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color if hover_color else bg_color
        self.fg_color = fg_color
        self.text_font = text_font
        
        self.rect_id = self.create_rounded_rect(2, 2, width-2, height-2, radius=18, fill=bg_color, outline="")
        self.text_id = self.create_text(width//2, height//2, text=text, fill=fg_color, font=self.text_font)
        
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.configure(cursor="hand2")
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        self.itemconfig(self.rect_id, fill=self.hover_color)
    
    def on_leave(self, e):
        self.itemconfig(self.rect_id, fill=self.bg_color)


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, bg=parent['bg'], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=parent['bg'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        # keep inner frame width synced to canvas so content spans available space
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(window_id, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        # enable click-drag scrolling for trackpad/mouse without wheel
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))

        # bind wheel only while hovered to keep touchpad focus in active frame
        self.canvas.bind("<Enter>", lambda e: self._bind_to_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_from_mousewheel())
    
    def _bind_to_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_from_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
    
    def _on_mousewheel(self, event):
        # Use fractional movement for smoother scrolling on touchpads and wheels
        if hasattr(event, "delta") and event.delta != 0:
            # Windows/macOS: delta is typically multiples of 120; even larger divisor for extra-smooth
            move = -event.delta / 9000
            first, _ = self.canvas.yview()
            self.canvas.yview_moveto(max(0, min(1, first + move)))
        elif event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
    
    def get_frame(self):
        return self.scrollable_frame


class StegoApp(TkinterDnD.Tk if HAS_DND else tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PixelGuard")
        self.geometry("1100x700")
        self.minsize(1000, 650)

        self.primary = "#FF0000"
        self.secondary = "#0b1f3a"  # dark blue sidebar
        self.background = "#f8fafc"
        self.card_bg = "#ffffff"
        self.text_dark = "#1e293b"
        self.text_light = "#64748b"
        self.border_color = "#e2e8f0"

        self.configure(bg=self.background)
        self.sidebar_width = 200
        self.sidebar_visible = True

        self.build_layout()

    def build_layout(self):
        self.root_container = tk.Frame(self, bg=self.background)
        self.root_container.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.root_container, bg=self.secondary, width=self.sidebar_width)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        self.main_area = tk.Frame(self.root_container, bg=self.background)
        self.main_area.pack(side="left", fill="both", expand=True)

        self.build_sidebar()
        self.build_topbar()
        self.build_pages()

    def build_sidebar(self):
        header = tk.Frame(self.sidebar, bg=self.secondary, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="PixelGuard", fg="#fef08a", bg=self.secondary, font=("Segoe UI", 20, "bold")).pack(pady=25)

        nav_frame = tk.Frame(self.sidebar, bg=self.secondary)
        nav_frame.pack(fill="both", expand=True, pady=20, padx=15)
        
        self.add_nav_button(nav_frame, "Home", self.show_home)
        self.add_nav_button(nav_frame, "Encrypt", self.show_encrypt)
        self.add_nav_button(nav_frame, "Decrypt", self.show_decrypt)

    def add_nav_button(self, parent, text, command):
        btn = tk.Label(
            parent, text=text, fg="white", bg=self.secondary, font=("Segoe UI", 12, "bold"),
            cursor="hand2", pady=12, padx=10, anchor="w", relief="flat"
        )
        btn.pack(fill="x", pady=6)
        
        bottom_border = tk.Frame(parent, bg=self.primary, height=2)
        bottom_border.pack(fill="x", padx=0)
        
        shadow = tk.Frame(parent, bg="#0d4a7a", height=1)
        shadow.pack(fill="x", padx=0)
        
        def on_enter(e):
            btn.config(fg=self.primary)
        def on_leave(e):
            btn.config(fg="white")
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", lambda e: command())

    def build_topbar(self):
        bar = tk.Frame(self.main_area, bg=self.background, height=60)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        menu_btn = tk.Label(
            bar, text="≡", fg=self.primary, bg=self.background, font=("Segoe UI", 24, "bold"),
            cursor="hand2", padx=20
        )
        menu_btn.pack(side="right")
        
        def on_enter(e):
            menu_btn.config(fg=self.secondary)
        def on_leave(e):
            menu_btn.config(fg=self.primary)
        
        menu_btn.bind("<Enter>", on_enter)
        menu_btn.bind("<Leave>", on_leave)
        menu_btn.bind("<Button-1>", lambda e: self.toggle_sidebar())

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side="left", fill="y", before=self.main_area)
        self.sidebar_visible = not self.sidebar_visible
        self.root_container.update_idletasks()

    def build_pages(self):
        self.pages = {
            "Home": tk.Frame(self.main_area, bg=self.background),
            "Encrypt": tk.Frame(self.main_area, bg=self.background),
            "Decrypt": tk.Frame(self.main_area, bg=self.background),
        }

        for p in self.pages.values():
            p.pack_forget()

        self.build_home_page()
        self.build_encrypt_page()
        self.build_decrypt_page()
        self.show_home()

    def build_home_page(self):
        page = self.pages["Home"]

        tk.Label(page, text="Image Steganography", bg=self.background, fg=self.text_dark, font=("Segoe UI", 32, "bold")).pack(pady=(120, 10))
        tk.Label(page, text="Secure message hiding in images", bg=self.background, fg=self.text_light, font=("Segoe UI", 13)).pack(pady=(0, 60))

        btns = tk.Frame(page, bg=self.background)
        btns.pack()

        light_cyan = "#cffafe"
        light_yellow = "#fef08a"
        hover_green = "#86efac"
        text_dark = self.text_dark
        RoundedButton(btns, "Encrypt Message", self.show_encrypt, light_cyan, text_dark, width=300, height=70, hover_color=hover_green, text_font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=20, pady=10)
        RoundedButton(btns, "Decrypt Message", self.show_decrypt, light_yellow, text_dark, width=300, height=70, hover_color=hover_green, text_font=("Segoe UI", 14, "bold")).grid(row=0, column=1, padx=20, pady=10)

    def build_encrypt_page(self):
        page = self.pages["Encrypt"]
        
        header_frame = tk.Frame(page, bg=self.background)
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        tk.Label(header_frame, text="Encrypt Message", bg=self.background, fg=self.text_dark, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(header_frame, text="Hide your secret message inside an image", bg=self.background, fg=self.text_light, font=("Segoe UI", 11)).pack(anchor="w")
        
        scroll_frame = ScrollableFrame(page, bg=self.background)
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0,20))
        card = self.card(scroll_frame.get_frame())

        self.encrypt_image_path = tk.StringVar(value="")
        self.section(card, "Image File")
        self.drag_drop_area(card, self.encrypt_image_path, self.select_encrypt_image, "encrypt")

        self.section(card, "Secret Message")
        self.encrypt_message = scrolledtext.ScrolledText(
            card, height=5, font=("Segoe UI", 11), relief="flat", bg=self.card_bg,
            fg=self.text_dark, insertbackground=self.primary, wrap="word"
        )
        self.encrypt_message.pack(fill="both", expand=True, pady=(0, 15), ipady=8, padx=1)

        self.section(card, "Encryption Key")
        self.encrypt_key = self.rounded_entry(card, show="●")

        self.section(card, "Channel Mode")
        self.encrypt_channel = tk.IntVar(value=3)
        self.channel_buttons(card, self.encrypt_channel)

        btn_frame = tk.Frame(card, bg=self.card_bg)
        btn_frame.pack(fill="x", pady=25)
        RoundedButton(btn_frame, "Encrypt Now", self.run_encrypt, "#bbf7d0", self.text_dark, width=220, height=50, hover_color="#e9d5ff").pack()

    def build_decrypt_page(self):
        page = self.pages["Decrypt"]
        
        header_frame = tk.Frame(page, bg=self.background)
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        tk.Label(header_frame, text="Decrypt Message", bg=self.background, fg=self.text_dark, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(header_frame, text="Reveal the hidden message from an image", bg=self.background, fg=self.text_light, font=("Segoe UI", 11)).pack(anchor="w")
        
        scroll_frame = ScrollableFrame(page, bg=self.background)
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0,20))
        card = self.card(scroll_frame.get_frame())

        self.decrypt_image_path = tk.StringVar(value="")
        self.section(card, "Encrypted Image")
        self.drag_drop_area(card, self.decrypt_image_path, self.select_decrypt_image, "decrypt")

        self.section(card, "Decryption Key")
        self.decrypt_key = self.rounded_entry(card, show="●")

        self.section(card, "Channel Mode")
        self.decrypt_channel = tk.IntVar(value=3)
        self.channel_buttons(card, self.decrypt_channel)

        btn_frame = tk.Frame(card, bg=self.card_bg)
        btn_frame.pack(fill="x", pady=25)
        RoundedButton(btn_frame, "Decrypt Now", self.run_decrypt, "#bbf7d0", self.text_dark, width=220, height=50, hover_color="#e9d5ff").pack()

    def card(self, parent):
        outer = tk.Frame(parent, bg=self.background)
        outer.pack(fill="both", expand=True, padx=40, pady=20)
        
        c = tk.Frame(outer, bg=self.card_bg, relief="flat", bd=0)
        c.pack(fill="both", expand=True, padx=0, pady=0)
        c.configure(padx=18, pady=22)
        
        border_canvas = tk.Canvas(c, height=1, bg=self.border_color, highlightthickness=0)
        border_canvas.pack(fill="x", side="bottom")
        
        return c

    def section(self, parent, text):
        section_bg = "#06b6d4"  # cyan
        label_frame = tk.Frame(parent, bg=section_bg)
        label_frame.pack(fill="x", pady=(20, 8))
        
        tk.Label(label_frame, text=text, bg=section_bg, fg="white", font=("Segoe UI", 11, "bold"), anchor="w", padx=15, pady=8).pack(fill="x")

    def rounded_entry(self, parent, **kwargs):
        entry_frame = tk.Frame(parent, bg=self.border_color, highlightthickness=0)
        entry_frame.pack(fill="x", pady=(0, 15), ipady=2, ipadx=2)
        
        entry = tk.Entry(entry_frame, font=("Segoe UI", 12), relief="flat", bg=self.card_bg, fg=self.text_dark, insertbackground=self.primary, borderwidth=0, **kwargs)
        entry.pack(fill="x", ipady=12, padx=2, pady=2)
        return entry

    def drag_drop_area(self, parent, var, browse_cmd, mode):
        container = tk.Frame(parent, bg=self.border_color, highlightthickness=0)
        container.pack(fill="x", pady=(0, 20), ipady=3, ipadx=3)
        
        area = tk.Frame(container, bg=self.card_bg)
        area.pack(fill="x", padx=3, pady=3)
        
        content = tk.Frame(area, bg=self.card_bg)
        content.pack(fill="x", padx=20, pady=20)
        
        top_row = tk.Frame(content, bg=self.card_bg)
        top_row.pack(fill="x", pady=(0, 15))
        
        icon_label = tk.Label(top_row, text="📁", bg=self.card_bg, fg=self.primary, font=("Segoe UI", 28))
        icon_label.pack(side="left", padx=(0, 15))
        
        text_frame = tk.Frame(top_row, bg=self.card_bg)
        text_frame.pack(side="left", fill="x", expand=True)
        
        text_label = tk.Label(text_frame, text="Drag & Drop Image Here", bg=self.card_bg, fg=self.text_light, font=("Segoe UI", 12), anchor="w", justify="left")
        text_label.pack(fill="x")
        
        filename_label = tk.Label(text_frame, text="", bg=self.card_bg, fg=self.text_light, font=("Segoe UI", 9), anchor="w", justify="left")
        filename_label.pack(fill="x")
        
        browse_frame = tk.Frame(content, bg=self.card_bg)
        browse_frame.pack()
        
        RoundedButton(browse_frame, "Browse Files", browse_cmd, self.primary, "white", width=160, height=40, hover_color=self.secondary).pack()
        
        def update_display(*args):
            path = var.get()
            if path and os.path.exists(path):
                filename = os.path.basename(path)
                text_label.config(text="✓ Image Selected", fg=self.primary, font=("Segoe UI", 12, "bold"))
                filename_label.config(text=filename, fg=self.primary, font=("Segoe UI", 10))
            else:
                text_label.config(text="Drag & Drop Image Here", fg=self.text_light, font=("Segoe UI", 12))
                filename_label.config(text="or click Browse Files below", fg=self.text_light, font=("Segoe UI", 9))
        
        var.trace_add("write", update_display)
        update_display()
        
        if HAS_DND:
            area.drop_target_register(DND_FILES)
            area.dnd_bind('<<Drop>>', lambda e: self.handle_drop(e, var))
            
            def on_drag_enter(e):
                area.config(bg="#ffe4e6")
                return "copy"
            
            def on_drag_leave(e):
                area.config(bg=self.card_bg)
            
            area.dnd_bind('<<DragEnter>>', on_drag_enter)
            area.dnd_bind('<<DragLeave>>', on_drag_leave)

    def handle_drop(self, event, var):
        files = self.tk.splitlist(event.data)
        if files:
            file_path = files[0].strip('{}')
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                var.set(file_path)
            else:
                messagebox.showerror("Error", "Please drop an image file (PNG, JPG, BMP)")

    def channel_buttons(self, parent, var):
        row = tk.Frame(parent, bg=self.card_bg)
        row.pack(fill="x", pady=10)

        def set_mode(m):
            var.set(m)
            update_buttons()
        
        def update_buttons():
            m = var.get()
            light_purple = "#e9d5ff"
            light_yellow = "#fef08a"
            if m == 1:
                btn1_canvas.itemconfig(rect1, fill=light_purple, outline=light_purple)
                btn1_canvas.itemconfig(txt1, fill=self.text_dark)
                btn3_canvas.itemconfig(rect3, fill=self.card_bg, outline=self.border_color)
                btn3_canvas.itemconfig(txt3, fill=self.text_light)
            else:
                btn1_canvas.itemconfig(rect1, fill=self.card_bg, outline=self.border_color)
                btn1_canvas.itemconfig(txt1, fill=self.text_light)
                btn3_canvas.itemconfig(rect3, fill=light_yellow, outline=light_yellow)
                btn3_canvas.itemconfig(txt3, fill=self.text_dark)

        btn1_canvas = tk.Canvas(row, width=150, height=45, bg=self.card_bg, highlightthickness=0)
        btn1_canvas.pack(side="left", padx=10)
        rect1 = self._create_rounded_rect(btn1_canvas, 0, 0, 150, 45, radius=18, fill=self.card_bg, outline=self.border_color, width=2)
        txt1 = btn1_canvas.create_text(75, 22, text="1-Channel", fill=self.text_light, font=("Segoe UI", 11, "bold"))
        btn1_canvas.bind("<Button-1>", lambda e: set_mode(1))
        btn1_canvas.configure(cursor="hand2")

        btn3_canvas = tk.Canvas(row, width=150, height=45, bg=self.card_bg, highlightthickness=0)
        btn3_canvas.pack(side="left", padx=10)
        rect3 = self._create_rounded_rect(btn3_canvas, 0, 0, 150, 45, radius=18, fill=self.card_bg, outline=self.border_color, width=2)
        txt3 = btn3_canvas.create_text(75, 22, text="3-Channel", fill="white", font=("Segoe UI", 11, "bold"))
        btn3_canvas.bind("<Button-1>", lambda e: set_mode(3))
        btn3_canvas.configure(cursor="hand2")
        
        update_buttons()

    def _create_rounded_rect(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

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

            if not img or not os.path.exists(img):
                raise ValueError("Please select an image file")
            if not msg:
                raise ValueError("Please enter a message")
            if not key:
                raise ValueError("Please enter an encryption key")

            out = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
            if not out:
                return

            embed_bits(img, build_bitstream(msg, key, mode), mode, out)
            messagebox.showinfo("Success", "Message encrypted successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_decrypt(self):
        try:
            img = self.decrypt_image_path.get()
            key = self.decrypt_key.get()

            if not img or not os.path.exists(img):
                raise ValueError("Please select an encrypted image")
            if not key:
                raise ValueError("Please enter the decryption key")

            bits = extract_bits(img, 3)
            msg, actual_mode = decode_message(bits, key)

            sel_mode = self.decrypt_channel.get()
            if sel_mode != actual_mode:
                messagebox.showwarning(
                    "Mode Mismatch",
                    f"Image was encoded in {actual_mode}-channel mode, not {sel_mode}-channel.\nShowing decoded message anyway."
                )

            messagebox.showinfo("Decrypted Message", msg)

        except Exception as e:
            messagebox.showerror("Error", str(e))

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
