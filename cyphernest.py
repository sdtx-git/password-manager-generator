import os
import pyAesCrypt
import csv
import secrets
import string
import customtkinter as ctk
from tkinter import messagebox
import random
import shutil

# Configurações
BUFFER_SIZE = 64 * 1024
CTK_THEME = "dark"  # "dark" ou "light"
ICON_SIZE = 20
DB_FILE = "db.aes"
BACKUP_FILE = "db.bak"

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Login")
        self.geometry("400x300")  # Set a default size for the login window
        self.resizable(False, False)
        self.on_success = on_success
        
        ctk.set_appearance_mode(CTK_THEME)
        
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self, 
            text="CypherNest", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, pady=(20, 5), sticky="ew")
        
        ctk.CTkLabel(
            self, 
            text="Sua Senha Segura", 
            font=ctk.CTkFont(size=14, weight="normal")
        ).grid(row=1, column=0, pady=(0, 20), sticky="ew")
        
        self.master_password_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Digite a senha mestra", 
            show="*"
        )
        self.master_password_entry.grid(row=2, column=0, padx=50, pady=10, sticky="ew")
        
        ctk.CTkButton(
            self, 
            text="Entrar", 
            command=self.attempt_login
        ).grid(row=3, column=0, padx=50, pady=10, sticky="ew")
        
        self.first_use_link = ctk.CTkButton(
            self, 
            text="Configurar Primeira Utilização", 
            fg_color="transparent",
            text_color="gray",
            command=self.first_use_setup
        )
        self.first_use_link.grid(row=4, column=0, pady=10)
        
        if not os.path.exists(DB_FILE):
            self.first_use_link.configure(text="Configurar Primeira Utilização")
    
    def attempt_login(self):
        master_password = self.master_password_entry.get()
        
        if not master_password:
            messagebox.showerror("Erro", "Por favor, insira a senha mestra")
            return
        
        try:
            self.decrypt_database(master_password)
            self.on_success(master_password)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Senha mestra incorreta ou arquivo corrompido: {str(e)}")
    
    def first_use_setup(self):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        
        new_master_password = ctk.CTkInputDialog(
            text="Defina sua senha mestra:", 
            title="Primeira Utilização"
        ).get_input()
        
        if not new_master_password:
            messagebox.showwarning("Aviso", "A senha mestra não pode ser vazia")
            return
        
        self.create_empty_database(new_master_password)
        self.on_success(new_master_password)
        self.destroy()
    
    def decrypt_database(self, master_password):
        if not os.path.exists(DB_FILE):
            raise FileNotFoundError("Arquivo de banco de dados não encontrado")
        
        temp_file = "temp_import.csv"
        pyAesCrypt.decryptFile(DB_FILE, temp_file, master_password, BUFFER_SIZE)
        os.remove(temp_file)
    
    def create_empty_database(self, master_password):
        temp_file = "temp_passwords.csv"
        
        with open(temp_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Serviço", "Usuário", "Senha"])
        
        pyAesCrypt.encryptFile(temp_file, DB_FILE, master_password, BUFFER_SIZE)
        os.remove(temp_file)

class PasswordManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CypherNest")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        self.withdraw()
        
        self.initialize_app = self._initialize_app  # Assign the method reference
        
        login_window = LoginWindow(self, self.initialize_app)
        login_window.grab_set()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)  # Adjusted row configuration
        
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="CypherNest",
            font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        self.generator_btn = ctk.CTkButton(
            self.sidebar,
            text="Gerar Senha",
            command=self.show_generator,
            fg_color="#2b579a" if CTK_THEME == "dark" else "#1f538d",
            hover_color="#1e4e8c")
        self.generator_btn.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.view_btn = ctk.CTkButton(
            self.sidebar,
            text="Minhas Senhas",
            command=self.show_password_manager,
            fg_color="transparent")
        self.view_btn.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        # Add "Alterar Senha Mestra" button to the bottom-left corner
        ctk.CTkButton(
            self.sidebar,
            text="Alterar Senha Mestra",
            command=self.change_master_password,
            fg_color="transparent").grid(row=5, column=0, padx=20, pady=10, sticky="sw")
        
        self.main_area = ctk.CTkFrame(self, corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        
        self.generator_page = self.create_generator_page()
        self.password_manager_page = self.create_password_manager_page()
        self.password_manager_page.grid_forget()
        
        self.status_bar = ctk.CTkLabel(
            self, 
            text="Pronto", 
            anchor="w",
            font=ctk.CTkFont(size=10))
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        # ...existing code...

    def _initialize_app(self, master_password):
        self.deiconify()
        self.master_password = master_password
        self.passwords = self.load_passwords(master_password)
        # ...existing code...

    def load_passwords(self, master_password):
        if not os.path.exists(DB_FILE):
            print("Arquivo db.aes não encontrado. Retornando lista vazia.")
            return []
        
        temp_file = "temp_import.csv"
        
        try:
            pyAesCrypt.decryptFile(DB_FILE, temp_file, master_password, BUFFER_SIZE)
            
            with open(temp_file, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)
                if header != ["Serviço", "Usuário", "Senha"]:
                    raise ValueError("Formato do arquivo inválido: cabeçalho incorreto")
                passwords = [row for row in reader]
            
            os.remove(temp_file)
            # Substituído por uma mensagem genérica
            print(f"Carregadas {len(passwords)} senhas do arquivo db.aes")
            return passwords
        except Exception as e:
            print(f"Erro ao carregar senhas: {str(e)}")
            messagebox.showerror("Erro", f"Falha ao carregar senhas: {str(e)}")
            return []

    def save_passwords(self):
        temp_file = "temp_passwords.csv"
        
        try:
            with open(temp_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Serviço", "Usuário", "Senha"])
                writer.writerows(self.passwords)
            
            pyAesCrypt.encryptFile(temp_file, DB_FILE, self.master_password, BUFFER_SIZE)
            
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, BACKUP_FILE)
                print(f"Backup criado em {BACKUP_FILE}")
            
            os.remove(temp_file)
            # Substituído por uma mensagem genérica
            print(f"Salvas {len(self.passwords)} senhas no arquivo db.aes")
            self.passwords = self.load_passwords(self.master_password)
        except Exception as e:
            print(f"Erro ao salvar senhas: {str(e)}")
            messagebox.showerror("Erro", f"Falha ao salvar senhas: {str(e)}")

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
        if new_mode == "dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
        
        self.update_theme_colors()
        self.status_bar.configure(text=f"Tema alterado para {new_mode}")

    def update_theme_colors(self):
        mode = ctk.get_appearance_mode()
        text_color = "white" if mode == "Dark" else "black"
        active_color = "#2b579a" if mode == "Dark" else "#1f538d"
        inactive_color = "transparent"
        inactive_text_color = "white" if mode == "Dark" else "black"
        
        self.logo_label.configure(text_color=text_color)
        self.generator_btn.configure(
            fg_color=active_color if self.generator_page.winfo_ismapped() else inactive_color,
            text_color=text_color if self.generator_page.winfo_ismapped() else inactive_text_color
        )
        self.view_btn.configure(
            fg_color=active_color if self.password_manager_page.winfo_ismapped() else inactive_color,
            text_color=text_color if self.password_manager_page.winfo_ismapped() else inactive_text_color
        )
        
        self.status_bar.configure(text_color=text_color)
        
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=text_color)
            elif isinstance(widget, ctk.CTkButton) and widget not in [self.generator_btn, self.view_btn]:
                widget.configure(text_color=inactive_text_color)
        
        for widget in self.generator_page.winfo_children() + self.password_manager_page.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=text_color)

    def create_generator_page(self):
        frame = ctk.CTkFrame(self.main_area)
        
        ctk.CTkLabel(frame, text="Gerador de Senhas Seguras", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 30))
        
        form_frame = ctk.CTkFrame(frame, fg_color="transparent")
        form_frame.pack(pady=10, padx=50, fill="x")
        
        ctk.CTkLabel(form_frame, text="Serviço/Descrição:").grid(row=0, column=0, sticky="e", padx=5, pady=10)
        self.service_entry = ctk.CTkEntry(form_frame)
        self.service_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        ctk.CTkLabel(form_frame, text="Usuário (opcional):").grid(row=1, column=0, sticky="e", padx=5, pady=10)
        self.user_entry = ctk.CTkEntry(form_frame)
        self.user_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=10)
        
        ctk.CTkLabel(form_frame, text="Tamanho da senha:").grid(row=2, column=0, sticky="e", padx=5, pady=10)
        self.length_slider = ctk.CTkSlider(form_frame, from_=8, to=32, number_of_steps=24)
        self.length_slider.set(16)
        self.length_slider.grid(row=2, column=1, sticky="ew", padx=5, pady=10)
        self.length_label = ctk.CTkLabel(form_frame, text="16 caracteres")
        self.length_label.grid(row=2, column=2, padx=5, pady=10)
        self.length_slider.configure(command=lambda v: self.length_label.configure(text=f"{int(float(v))} caracteres"))
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        self.generate_btn = ctk.CTkButton(
            btn_frame, 
            text="Gerar e Armazenar Senha", 
            width=200,
            command=self.generate_and_store_password)
        self.generate_btn.pack(pady=10)
        
        self.generated_password_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.generated_password_frame.pack(pady=20, fill="x", padx=50)
        
        ctk.CTkLabel(self.generated_password_frame, text="Sua nova senha:").pack(side="left", padx=5)
        self.password_display = ctk.CTkLabel(
            self.generated_password_frame, 
            text="", 
            font=ctk.CTkFont(family="Courier", size=14),
            anchor="w")
        self.password_display.pack(side="left", fill="x", expand=True, padx=5)
        
        self.copy_btn = ctk.CTkButton(
            self.generated_password_frame,
            text="Copiar",
            width=80,
            command=self.copy_to_clipboard)
        self.copy_btn.pack(side="right", padx=5)
        
        return frame

    def create_password_manager_page(self):
        frame = ctk.CTkFrame(self.main_area)
        
        ctk.CTkLabel(frame, text="Senhas Armazenadas", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        
        top_bar = ctk.CTkFrame(frame, fg_color="transparent")
        top_bar.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(top_bar, text="Buscar Serviço:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(top_bar)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_passwords_list(self.search_entry.get()))
        
        ctk.CTkButton(
            top_bar,
            text="+",
            width=40,
            command=self.add_custom_password
        ).pack(side="right", padx=5)
        
        self.passwords_list = ctk.CTkScrollableFrame(frame, height=300)
        self.passwords_list.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkButton(
            frame, 
            text="Voltar ao Gerador", 
            command=self.show_generator).pack(pady=20)
        
        return frame

    def add_custom_password(self):
        add_window = ctk.CTkToplevel(self)
        add_window.title("Adicionar Senha")
        add_window.geometry("300x300")  # Sophisticated size for better usability
        add_window.resizable(False, False)
        add_window.transient(self)
        
        add_window.after(100, lambda: self._set_grab(add_window))
        
        mode = ctk.get_appearance_mode()
        text_color = "white" if mode == "Dark" else "black"
        
        form_frame = ctk.CTkFrame(add_window, fg_color="transparent")
        form_frame.pack(pady=20, padx=30, fill="x")
        
        ctk.CTkLabel(form_frame, text="Serviço:", text_color=text_color, font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, sticky="e", padx=10, pady=10)
        service_entry = ctk.CTkEntry(form_frame, width=250)
        service_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        ctk.CTkLabel(form_frame, text="Usuário:", text_color=text_color, font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="e", padx=10, pady=10)
        user_entry = ctk.CTkEntry(form_frame, width=250)
        user_entry.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        ctk.CTkLabel(form_frame, text="Senha:", text_color=text_color, font=ctk.CTkFont(size=14)).grid(
            row=2, column=0, sticky="e", padx=10, pady=10)
        password_entry = ctk.CTkEntry(form_frame, show="*", width=250)
        password_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        show_password_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            form_frame,
            text="Mostrar Senha",
            variable=show_password_var,
            command=lambda: password_entry.configure(show="" if show_password_var.get() else "*"),
            text_color=text_color
        ).grid(row=3, column=1, sticky="w", pady=10)
        
        # Add "Salvar" button with better alignment
        ctk.CTkButton(
            add_window,
            text="Salvar",
            command=lambda: self.save_new_password(
                service_entry.get(), 
                user_entry.get(), 
                password_entry.get(), 
                add_window
            ),
            width=150,
            fg_color="#2b579a" if mode == "Dark" else "#1f538d",
            hover_color="#1e4e8c"
        ).pack(pady=20)

    def save_new_password(self, service, user, password, window):
        if not service or not password:
            messagebox.showerror("Erro", "O serviço e a senha não podem estar vazios!")
            return
        
        self.passwords.append((service, user or "N/A", password))
        self.save_passwords()
        self.update_passwords_list(self.search_entry.get() if self.password_manager_page.winfo_ismapped() else "")
        self.status_bar.configure(text=f"Senha para {service} adicionada com sucesso!")
        window.destroy()
    
    def show_generator(self):
        self.password_manager_page.grid_forget()
        self.generator_page.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.update_theme_colors()
    
    def show_password_manager(self):
        self.generator_page.grid_forget()
        self.password_manager_page.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.update_passwords_list()
        self.update_theme_colors()
    
    def update_passwords_list(self, search_query=""):
        for widget in self.passwords_list.winfo_children():
            widget.destroy()
        
        filtered_passwords = [
            (idx, (service, user, password))
            for idx, (service, user, password) in enumerate(self.passwords)
            if search_query.lower() in service.lower()
        ]
        # Removido os prints que exibiam as senhas
        
        if not filtered_passwords:
            ctk.CTkLabel(
                self.passwords_list, 
                text="Nenhuma senha encontrada" if search_query else "Nenhuma senha armazenada",
                font=ctk.CTkFont(size=14)).pack(pady=50)
            return
        
        mode = ctk.get_appearance_mode()
        text_color = "white" if mode == "Dark" else "black"
        
        for idx, (service, user, password) in filtered_passwords:
            card = ctk.CTkFrame(self.passwords_list, border_width=1, corner_radius=10)
            card.pack(fill="x", pady=8, padx=10)
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=5)
            
            service_btn = ctk.CTkButton(
                info_frame,
                text=service,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                text_color=text_color,
                anchor="w",
                command=lambda p=password: self.copy_password_to_clipboard(p))
            service_btn.pack(side="left", padx=5)
            
            ctk.CTkLabel(
                info_frame, 
                text=f"Usuário: {user}",
                font=ctk.CTkFont(size=12),
                text_color=text_color).pack(side="left", padx=15)
            
            delete_btn = ctk.CTkButton(
                info_frame,
                text="Excluir",
                width=80,
                fg_color="red",
                hover_color="darkred",
                command=lambda i=idx: self.delete_password(i))
            delete_btn.pack(side="right", padx=5)
            
            edit_btn = ctk.CTkButton(
                info_frame,
                text="Editar",
                width=80,
                command=lambda i=idx: self.edit_password(i))
            edit_btn.pack(side="right", padx=5)
            
            toggle_btn = ctk.CTkButton(
                info_frame,
                text="Mostrar",
                width=80)
            toggle_btn.pack(side="right", padx=5)
            toggle_btn.configure(command=lambda s=service, u=user, p=password, c=card: self.toggle_password_details(s, u, p, c))
    
    def toggle_password_details(self, service, user, password, card):
        info_frame = card.winfo_children()[0]
        toggle_btn = info_frame.winfo_children()[-1]
        
        if hasattr(card, 'details_frame'):
            card.details_frame.destroy()
            del card.details_frame
            toggle_btn.configure(text="Mostrar")
        else:
            mode = ctk.get_appearance_mode()
            text_color = "white" if mode == "Dark" else "black"
            
            details_frame = ctk.CTkFrame(card, fg_color="transparent")
            details_frame.pack(fill="x", padx=10, pady=(0, 10))
            card.details_frame = details_frame
            
            pass_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            pass_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(pass_frame, text="Senha:", text_color=text_color).pack(side="left", padx=5)
            password_label = ctk.CTkLabel(
                pass_frame, 
                text="*" * len(password),
                font=ctk.CTkFont(family="Courier"),
                text_color=text_color)
            password_label.pack(side="left", padx=5)
            
            toggle_text = ctk.StringVar(value="Mostrar Senha")
            toggle_btn_details = ctk.CTkButton(
                pass_frame,
                textvariable=toggle_text,
                width=120,
                command=lambda: self.toggle_password_visibility(password, password_label, toggle_text))
            toggle_btn_details.pack(side="right", padx=5)
            
            toggle_btn.configure(text="Ocultar")
    
    def toggle_password_visibility(self, password, label, toggle_text):
        if toggle_text.get() == "Mostrar Senha":
            label.configure(text=password)
            toggle_text.set("Ocultar Senha")
        else:
            label.configure(text="*" * len(password))
            toggle_text.set("Mostrar Senha")
    
    def edit_password(self, index):
        service, user, password = self.passwords[index]
        
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Editar Senha")
        edit_window.geometry("")  # Automatically adjust to content
        edit_window.resizable(False, False)
        edit_window.transient(self)
        
        edit_window.after(100, lambda: self._set_grab(edit_window))
        
        mode = ctk.get_appearance_mode()
        text_color = "white" if mode == "Dark" else "black"
        
        ctk.CTkLabel(
            edit_window,
            text="Editar Senha",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=text_color
        ).pack(pady=(20, 10))
        
        form_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        form_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(form_frame, text="Serviço:", text_color=text_color).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        service_entry = ctk.CTkEntry(form_frame)
        service_entry.insert(0, service)
        service_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Usuário:", text_color=text_color).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        user_entry = ctk.CTkEntry(form_frame)
        user_entry.insert(0, user)
        user_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Senha:", text_color=text_color).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        password_entry = ctk.CTkEntry(form_frame, show="*")
        password_entry.insert(0, password)
        password_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        show_password_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            form_frame,
            text="Mostrar Senha",
            variable=show_password_var,
            command=lambda: password_entry.configure(show="" if show_password_var.get() else "*"),
            text_color=text_color
        ).grid(row=3, column=1, sticky="w", pady=5)
        
        ctk.CTkLabel(form_frame, text="Senha Mestra:", text_color=text_color).grid(row=4, column=0, sticky="e", padx=5, pady=5)
        master_password_entry = ctk.CTkEntry(form_frame, show="*")
        master_password_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkButton(
            edit_window,
            text="Salvar",
            command=lambda: self.save_edited_password(
                index, 
                service_entry.get(), 
                user_entry.get(), 
                password_entry.get(), 
                master_password_entry.get(), 
                edit_window
            )
        ).pack(pady=20)

    def _set_grab(self, window):
        try:
            if window.winfo_exists():
                window.grab_set()
        except Exception as e:
            print(f"Erro ao definir grab_set: {str(e)}")
    
    def save_edited_password(self, index, service, user, password, master_password_input, window):
        if not service:
            messagebox.showerror("Erro", "O serviço não pode estar vazio!")
            return
        
        if master_password_input != self.master_password:
            messagebox.showerror("Erro", "Senha mestra incorreta!")
            return
        
        self.passwords[index] = (service, user or "N/A", password)
        self.save_passwords()
        self.update_passwords_list(self.search_entry.get() if self.password_manager_page.winfo_ismapped() else "")
        self.status_bar.configure(text=f"Senha para {service} editada com sucesso!")
        window.destroy()
    
    def delete_password(self, index):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta senha?"):
            del self.passwords[index]
            self.save_passwords()
            self.update_passwords_list(self.search_entry.get() if self.password_manager_page.winfo_ismapped() else "")
            self.status_bar.configure(text="Senha excluída com sucesso!")
    
    def change_master_password(self):
        current_password = ctk.CTkInputDialog(
            text="Digite a senha mestra atual:",
            title="Autenticação").get_input()
        
        if current_password != self.master_password:
            messagebox.showerror("Erro", "Senha mestra incorreta!")
            return
        
        new_password = ctk.CTkInputDialog(
            text="Digite a nova senha mestra:",
            title="Nova Senha").get_input()
        
        if not new_password:
            messagebox.showwarning("Aviso", "A nova senha não pode ser vazia.")
            return
        
        temp_passwords = self.passwords.copy()
        
        self.master_password = new_password
        self.passwords = temp_passwords
        self.save_passwords()
        
        self.status_bar.configure(text="Senha mestra alterada com sucesso!")
    
    def copy_password_to_clipboard(self, password):
        try:
            self.clipboard_clear()
            self.clipboard_append(password)
            self.status_bar.configure(text="Senha copiada para a área de transferência!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao copiar a senha: {str(e)}")
    
    def generate_password(self, length=16):
        if length < 4:
            length = 4
        
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        punctuation = string.punctuation
        
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(punctuation)
        ]
        
        all_chars = uppercase + lowercase + digits + punctuation
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        random.shuffle(password)
        return ''.join(password)
    
    def generate_and_store_password(self):
        try:
            length = int(self.length_slider.get())
            service = self.service_entry.get()
            user = self.user_entry.get() or "N/A"
            
            if not service:
                messagebox.showerror("Erro", "Por favor, insira a descrição do serviço.")
                return
            
            password = self.generate_password(length)
            
            self.passwords.append((service, user, password))
            
            self.save_passwords()
            
            self.password_display.configure(text=password)
            self.status_bar.configure(text=f"Senha para {service} gerada e armazenada com sucesso!")
            
            self.update_passwords_list()
            
            self.service_entry.delete(0, "end")
            self.user_entry.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    
    def copy_to_clipboard(self):
        password = self.password_display.cget("text")
        if password:
            self.copy_password_to_clipboard(password)

if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()
