from encrypt import build_bitstream , embed_bits
from decrypt import extract_bits , decode_message

import tkinter as tk 
from tkinter import ttk
from tkinter import filedialog , messagebox
class StegoApp(tk.Tk):

    def __init__(self):
        super().__init__()

        #Windows setup
        self.title("Image Steganography Tool")
        self.geometry("1000x650")
        self.minsize(900, 600)

        self.state("normal") #To allow maxmize / ResiZe

        self.bg_color = "#f4f6f8"
        self.sidebar_color = "#1f2933"
        self.accent_color = "#4f46e5"
        self.text_color = "#111827"

        self.configure(bg=self.bg_color)

        # sidebar state 
        self.sidebar_visible = True 

        self.build_layout()















    def build_layout(self):
        # Root Container 
        self.root_container = tk.Frame(self , bg=self.bg_color)
        self.root_container.pack(fill="both", expand=True)

        # Sidebar LEFT

        self.sidebar = tk.Frame(
            self.root_container,
            bg=self.sidebar_color,
            width = 220
        )
        self.sidebar.pack(side="left", fill="y")

        # Main (RRight)
        self.main_area = tk.Frame(
            self.root_container,
            bg=self.bg_color
        )
        self.main_area.pack(side="right", fill="both", expand=True)

        self.build_sidebar()
        self.build_topbar()
        self.build_pages()

















    def build_sidebar(self):
        #App name 
        title = tk.Label(
            self.sidebar,
            text="StegoTool",
            fg="white",
            bg=self.sidebar_color,
            font =("Segoe UI" , 16 , "bold")
        )
        title.pack(pady = (20 , 30))

        #Navigation buttons

        self.nav_buttons = {}

        self.add_nav_button("Home" , self.show_home)
        self.add_nav_button("Encrypt" , self.show_encrypt)
        self.add_nav_button("Decrypt" , self.show_decrypt)















    def add_nav_button(self , text , command):
        btn = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            bg=self.sidebar_color,
            fg="white",
            activebackground="#374151",
            activeforeground="white",
            relief="flat",
            anchor="w",
            padx=20,
            font=("Segoe UI" , 12)
        )
        btn.pack(fill="x" , pady=4)
        self.nav_buttons[text] = btn
















    def build_topbar(self):
        self.top_bar = tk.Frame(self.main_area , bg=self.bg_color , height=50)
        self.top_bar.pack(fill="x")

        toggle_btn = tk.Button(
            self.top_bar,
            text = "☰",
            command=self.toggle_sidebar,
            bg=self.bg_color,
            fg=self.text_color,
            relief="flat",
            font=("Segoe UI" , 16)

        )
        toggle_btn.pack(side="left", padx=10 , pady=10)












    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
        else:
            self.sidebar.pack(side="left" , fill="y")
            self.sidebar_visible = True









    def build_pages(self):
        self.pages = {}

        self.pages["Home"] = tk.Frame(self.main_area , bg=self.bg_color)
        self.pages["Encrypt"] = tk.Frame(self.main_area , bg=self.bg_color)
        self.pages["Decrypt"] = tk.Frame(self.main_area , bg=self.bg_color)

        for page in self.pages.values():
            page.pack(fill="both" , expand=True)
        
        self.build_home_page()
        self.build_encrypt_page()
        self.build_decrypt_page()

        self.show_home()










    def build_home_page(self):
        page = self.pages["Home"]

        title = tk.Label(
            page,
            text = "Image Steganography Tool",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI" , 26 , "bold")   
        )
        title.pack(pady=(120,10))

        subtitle = tk.Label(
            page,
            text = "Secure Message hiding using encryption and mathematics",
            bg=self.bg_color,
            fg="#6b7280",
            font=("Segoe UI" , 12 )
        )
        subtitle.pack(pady=(0,40))

        btn_frame = tk.Frame(page , bg=self.bg_color)
        btn_frame.pack()

        enc_btn = tk.Button(
            btn_frame,
            text="Encrypt",
            command=self.show_encrypt,
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI" , 14 , "bold"),
            padx=40,
            pady=12,
            relief="flat"
        )
        enc_btn.grid(row=0 , column=0 , padx=15)

        dec_btn = tk.Button(
            btn_frame,
            text ="Decrypt",
            command=self.show_decrypt,
            bg="#374151",
            fg="white",
            font=("Segoe UI" , 14),
            padx=40,
            pady=12,
            relief="flat"
        )
        dec_btn.grid(row=0 , column=1 , padx=15)













    def build_encrypt_page(self):
        page = self.pages["Encrypt"]
        
        container = tk.Frame(page, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=40, pady=30)

        img_frame = tk.Frame(container , bg=self.bg_color)
        img_frame.pack(fill="x" , pady=(0,20))

        self.encrypt_image_path = tk.StringVar(value="No image selected")

        select_img_btn = tk.Button(
            img_frame,
            text="Select Image",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI" , 11),
            padx=20,
            pady=8,
            relief="flat",
            command=self.select_encrypt_image
        )
        select_img_btn.pack(side="left")

        img_label = tk.Label(
            img_frame,
            textvariable=self.encrypt_image_path,
            bg=self.bg_color,
            fg="#374151",
            font=("Segoe UI" , 10)
        )
        img_label.pack(side="left", padx=15)
        msg_label = tk.Label(
            container,
            text="Message",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI" , 11, "bold")
            )
        msg_label.pack(anchor="w")

        #Message text box 
        self.encrypt_message = tk.Text(
            container,
            height = 6,
            font=("Segoe UI" , 11),
            wrap="word"
        )
        self.encrypt_message.pack(fill="x" , pady=(5,25))

        key_label = tk.Label(
            container,
            text="Encryption Key",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI" , 11, "bold")
        )
        key_label.pack(anchor="w")

        self.encrypt_key = tk.Entry(
            container,
            show="●",
            font=("Segoe UI" , 11)
        )
        self.encrypt_key.pack(fill="x" , pady=(5,25))

        
        channel_label = tk.Label(
            container,
            text="Channel Mode",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI", 11, "bold")
        )
        channel_label.pack(anchor="w")

        channel_frame = tk.Frame(container, bg=self.bg_color)
        channel_frame.pack(fill="x", pady=(10, 25))

        self.encrypt_channel = tk.IntVar(value=3)

        def select_channel(mode):
            self.encrypt_channel.set(mode)
            btn_1.config(bg=self.accent_color if mode == 1 else "#e5e7eb",
                         fg="white" if mode == 1 else self.text_color)
            btn_3.config(bg=self.accent_color if mode == 3 else "#e5e7eb",
                         fg="white" if mode == 3 else self.text_color)

        btn_1 = tk.Button(
            channel_frame,
            text="1-Channel",
            bg="#e5e7eb",
            font=("Segoe UI", 11),
            padx=30,
            pady=10,
            relief="flat",
            command=lambda: select_channel(1)
        )
        btn_1.pack(side="left", padx=10)

        btn_3 = tk.Button(
            channel_frame,
            text="3-Channel",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI", 11),
            padx=30,
            pady=10,
            relief="flat",
            command=lambda: select_channel(3)
        )
        btn_3.pack(side="left", padx=10)

        encrypt_btn = tk.Button(
            container,
            text="Encrypt",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI" , 13 , "bold"),
            padx=40,
            pady=12,
            relief="flat",
            command=self.run_encrypt
        )
        encrypt_btn.pack(pady=20)

        













    def select_encrypt_image(self):
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes = [("image files" , "*.png;*.jpg;*.jpeg;*.bmp"), ("All files" , "*.*")]
        )
        if file_path:
            self.encrypt_image_path.set(file_path)





    def run_encrypt(self):
        try:
            image_path = self.encrypt_image_path.get()
            message = self.encrypt_message.get("1.0" , "end").strip()
            key = self.encrypt_key.get()
            mode = self.encrypt_channel.get()

            if not image_path or image_path == "No image selected":
                messagebox.showerror("Error" , "Please select an image.")
                return
            if not message:
                messagebox.showerror("Error" , "Please enter a message to hide.")
                return
            if not key:
                messagebox.showerror("Error" , "Please enter an encryption key.")
                return
            output_path = filedialog.asksaveasfilename(
                title="Save Encrypted Image",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")]
            )

            if not output_path:
                return 
            bitstream = build_bitstream(message , key , mode)
            embed_bits(image_path , bitstream , mode , output_path)

            messagebox.showinfo("Success" , f"Message encrypted successfully")
        
        except Exception as e:
            messagebox.showerror("Error", str(e))













    def build_decrypt_page(self):
        page = self.pages["Decrypt"]

        container = tk.Frame(page , bg=self.bg_color)
        container.pack(fill="both" , expand=True , padx=40 , pady = 30)

        #image selection 
        img_frame = tk.Frame(container , bg=self.bg_color)
        img_frame.pack(fill="x" , pady=(0,20))

        self.decrypt_image_path = tk.StringVar(value="No image selected")

        select_img_btn = tk.Button(
            img_frame,
            text="Select Image",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI" , 11),
            padx=20,
            pady=8,
            relief="flat",
            command=self.select_decrypt_image
        )
        select_img_btn.pack(side="left")

        img_label = tk.Label(
            img_frame,
            textvariable=self.decrypt_image_path,
            bg=self.bg_color,
            fg="#374151",
            font=("Segoe UI" , 10)
        )
        img_label.pack(side="left", padx=15)

        #Decryption key

        key_label = tk.Label(
            container,
            text="Decryption Key",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI" , 11, "bold")
        )
        key_label.pack(anchor="w")

        self.decrypt_key = tk.Entry(
            container,
            show="●",
            font=("Segoe UI" , 11)
        )
        self.decrypt_key.pack(fill="x" , pady=(5,25))

        #Channel Selection
        channel_label = tk.Label(
            container,
            text="Channel Mode",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI", 11, "bold")
        )
        channel_label.pack(anchor="w")

        channel_frame = tk.Frame(container, bg=self.bg_color)
        channel_frame.pack(fill="x", pady=(10, 25))

        self.decrypt_channel = tk.IntVar(value=3)

        btn_1 = tk.Button(
            channel_frame,
            text="1-Channel",
            bg="#e5e7eb",
            padx =30,
            pady=10,
            relief="flat",
            command=lambda: self.decrypt_channel.set(1)
        )
        btn_1.pack(side="left", padx=10)

        btn_3 = tk.Button(
            channel_frame,
            text="3-Channel",
            bg=self.accent_color,
            fg="white",
            padx =30,
            pady=10,
            relief="flat",
            command=lambda: self.decrypt_channel.set(3)
        )
        btn_3.pack(side="left", padx=10)

        #Decrypt button

        decrypt_btn = tk.Button(
            container,
            text="Decrypt",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI" , 13 , "bold"),
            padx=40,
            pady=12,
            relief="flat",
            command=self.run_decrypt
        )
        decrypt_btn.pack(pady=20)

    def select_decrypt_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes = [("image files" , "*.png;*.jpg;*.jpeg;*.bmp"), ("All files" , "*.*")]
        )
        if file_path:
            self.decrypt_image_path.set(file_path)
    def run_decrypt(self):
        try:
            image_path = self.decrypt_image_path.get()
            key = self.decrypt_key.get()
            mode = self.decrypt_channel.get()

            if not image_path or image_path == "No image selected":
                messagebox.showerror("Error" , "Please select an image.")
                return
            if not key:
                messagebox.showerror("Error" , "Please enter a decryption key.")
                return  
            
            bits = extract_bits(image_path , 3) # mode replaced with 3
            message , actual_mode = decode_message(bits , key) # Decode message and get actual mode

            if mode != actual_mode:
                messagebox.showerror(
                    "Error" ,
                    f"Wrong Channel Select. \n This image was encoded in mode {actual_mode} - Channel."
                )
                return
            messagebox.showinfo("Decrypted Message" , message)
        except Exception as e:
            messagebox.showerror("Error", str(e))








    def show_home(self):
        self.show_page("Home")















    def show_encrypt(self):
        self.show_page("Encrypt")














    def show_decrypt(self):
        self.show_page("Decrypt")

















    def show_page(self , page_name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill="both",expand=True)
















    
if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()
