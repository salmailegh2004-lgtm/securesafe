# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from backend import SecureSafeBackend


# --- PALETTE NORD THEME ---
COLORS = {
    "bg_dark": "#2E3440",
    "bg_sidebar": "#3B4252",
    "card_bg": "#434C5E",
    "accent": "#88C0D0",
    "accent_hover": "#81A1C1",
    "danger": "#BF616A",
    "success": "#A3BE8C",
    "warning": "#EBCB8B",
    "text_main": "#ECEFF4",
    "text_sub": "#D8DEE9",
    "input_bg": "#4C566A"
}


# --- BOUTONS PERSONNALISÉS ---
class ModernButton(tk.Button):
    def __init__(self, master, **kw):
        kw["bg"] = kw.get("bg", COLORS["accent"])
        kw["fg"] = kw.get("fg", COLORS["bg_dark"])
        kw["font"] = kw.get("font", ("Segoe UI", 10, "bold"))
        kw["relief"] = "flat"
        kw["activebackground"] = COLORS["accent_hover"]
        kw["activeforeground"] = COLORS["bg_dark"]
        kw["cursor"] = "hand2"
        kw["pady"] = 5
        super().__init__(master, **kw)


class SidebarButton(tk.Button):
    def __init__(self, master, text, command):
        super().__init__(
            master,
            text=f"  {text}",
            command=command,
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_sub"],
            font=("Segoe UI", 11),
            relief="flat",
            anchor="w",
            activebackground=COLORS["card_bg"],
            activeforeground=COLORS["text_main"],
            bd=0,
            padx=20,
            pady=12,
            cursor="hand2",
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self["bg"] = COLORS["card_bg"]
        self["fg"] = COLORS["text_main"]

    def on_leave(self, e):
        self["bg"] = COLORS["bg_sidebar"]
        self["fg"] = COLORS["text_sub"]


# ---------------------- INTERFACE PRINCIPALE ----------------------
class SecureSafeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureSafe Pro v2")
        self.root.geometry("1100x700")
        self.root.configure(bg=COLORS["bg_dark"])

        self.backend = SecureSafeBackend()

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure("TScrollbar", background=COLORS["card_bg"], troughcolor=COLORS["bg_dark"], borderwidth=0)

        self.show_login_screen()

    # ------------------------------------------------
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ------------------------------------------------
    # ------------------- LOGIN ----------------------
    # ------------------------------------------------
    def show_login_screen(self):
        self.clear_screen()

        frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="🔒 SecureSafe", font=("Segoe UI", 32, "bold"),
                 bg=COLORS["bg_dark"], fg=COLORS["accent"]).pack(pady=10)
        tk.Label(frame, text="Accès Sécurisé", font=("Segoe UI", 12),
                 bg=COLORS["bg_dark"], fg=COLORS["text_sub"]).pack(pady=10)

        self.create_entry(frame, "Nom d'utilisateur", "username")
        self.create_entry(frame, "Mot de passe Maître", "master", show="●")

        btn_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        btn_frame.pack(pady=30)

        ModernButton(btn_frame, text="SE CONNECTER", width=15, command=self.perform_login).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Créer un compte", bg=COLORS["bg_dark"], fg=COLORS["accent"],
            font=("Segoe UI", 10, "underline"), bd=0, cursor="hand2",
            activebackground=COLORS["bg_dark"], command=self.show_create_account
        ).pack(side="left", padx=10)

    def create_entry(self, parent, text, name, show=""):
        tk.Label(parent, text=text, font=("Segoe UI", 10),
                 bg=COLORS["bg_dark"], fg=COLORS["text_sub"]).pack(anchor="w")
        entry = tk.Entry(parent, font=("Segoe UI", 11),
                         bg=COLORS["input_bg"], fg=COLORS["text_main"],
                         show=show, relief="flat", insertbackground="white", width=35)
        entry.pack(ipady=5)
        setattr(self, f"{name}_entry", entry)

    def perform_login(self):
        username = self.username_entry.get()
        master = self.master_entry.get()

        success, msg = self.backend.login(username, master)
        if success:
            self.show_main_interface()
        else:
            messagebox.showerror("Erreur", msg)

    # ------------------------------------------------
    # ------------------- CREATE ACCOUNT -------------
    # ------------------------------------------------
    def show_create_account(self):
        self.clear_screen()

        frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="✨ Nouveau Compte", font=("Segoe UI", 26, "bold"),
                 bg=COLORS["bg_dark"], fg=COLORS["accent"]).pack(pady=10)

        self.create_entry(frame, "Nom d'utilisateur", "new_user")
        self.create_entry(frame, "Mot de passe Maître", "new_master", show="●")
        self.create_entry(frame, "Confirmer le mot de passe", "confirm_master", show="●")

        ModernButton(frame, text="CRÉER LE COMPTE", command=self.perform_create).pack(pady=20)

        tk.Button(frame, text="Retour", fg=COLORS["text_sub"], bg=COLORS["bg_dark"],
                  bd=0, cursor="hand2", command=self.show_login_screen).pack()

    def perform_create(self):
        u = self.new_user_entry.get()
        p = self.new_master_entry.get()
        c = self.confirm_master_entry.get()

        if not u or not p:
            messagebox.showerror("Erreur", "Tous les champs sont requis.")
            return
        if p != c:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
            return

        success, msg = self.backend.create_account(u, p)
        if success:
            messagebox.showinfo("Succès", msg)
            self.show_login_screen()
        else:
            messagebox.showerror("Erreur", msg)

    # ------------------------------------------------
    # --------------------- MAIN INTERFACE -----------
    # ------------------------------------------------
    def show_main_interface(self):
        self.clear_screen()

        sidebar = tk.Frame(self.root, width=250, bg=COLORS["bg_sidebar"])
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        user_frame = tk.Frame(sidebar, bg=COLORS["bg_sidebar"])
        user_frame.pack(pady=20)

        tk.Label(user_frame, text="👤", font=("Arial", 30),
                 bg=COLORS["bg_sidebar"], fg=COLORS["accent"]).pack()
        tk.Label(user_frame, text=self.backend.current_user, font=("Segoe UI", 14, "bold"),
                 bg=COLORS["bg_sidebar"], fg=COLORS["text_main"]).pack()

        SidebarButton(sidebar, "Mes mots de passe", lambda: self.switch_page("dashboard")).pack(fill="x")
        SidebarButton(sidebar, "Ajouter un compte", lambda: self.switch_page("add")).pack(fill="x")

        SidebarButton(sidebar, "⚙️ Paramètres", lambda: self.switch_page("settings")).pack(fill="x")

        tk.Button(sidebar, text="  Déconnexion", bg=COLORS["danger"], fg="white",
                  font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2",
                  command=self.logout).pack(side="bottom", fill="x")

        self.content_area = tk.Frame(self.root, bg=COLORS["bg_dark"])
        self.content_area.pack(fill="both", expand=True)

        self.switch_page("dashboard")

    def switch_page(self, page):
        for w in self.content_area.winfo_children():
            w.destroy()
        if page == "dashboard":
            self.render_dashboard()
        elif page == "add":
            self.render_add_form()
        
        elif page == "settings":
            self.render_settings()

    # ------------------------------------------------
    # ------------------- DASHBOARD ------------------
    # ------------------------------------------------
    def render_dashboard(self):
        header = tk.Frame(self.content_area, bg=COLORS["bg_dark"])
        header.pack(fill="x", pady=20, padx=20)

        tk.Label(header, text="Mes Mots de Passe", font=("Segoe UI", 20, "bold"),
                 bg=COLORS["bg_dark"], fg=COLORS["text_main"]).pack(side="left")

        search_var = tk.StringVar()
        search_var.trace("w", lambda *_: self.filter_passwords(search_var))

        tk.Entry(header, textvariable=search_var, bg=COLORS["input_bg"], fg="white",
                 insertbackground="white", width=25).pack(side="right")

        container = tk.Frame(self.content_area, bg=COLORS["bg_dark"])
        container.pack(fill="both", expand=True, padx=20)

        canvas = tk.Canvas(container, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.all_passwords = self.backend.get_all_passwords()
        self.populate_passwords(self.all_passwords)

    def filter_passwords(self, sv):
        q = sv.get().lower()
        filtered = [p for p in self.all_passwords if q in p["service"].lower() or q in p["username"].lower()]
        self.populate_passwords(filtered)

    def populate_passwords(self, passwords):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        if not passwords:
            tk.Label(self.scrollable_frame, text="Aucun résultat",
                     bg=COLORS["bg_dark"], fg=COLORS["text_sub"]).pack(pady=20)
            return
        for pwd in passwords:
            self.create_password_card(pwd)

    def create_password_card(self, data):
        card = tk.Frame(self.scrollable_frame, bg=COLORS["card_bg"], pady=10, padx=15)
        card.pack(fill="x", pady=5)

        info = tk.Frame(card, bg=COLORS["card_bg"])
        info.pack(side="left", fill="both", expand=True)

        tk.Label(info, text=data["service"], font=("Segoe UI", 12, "bold"),
                 bg=COLORS["card_bg"], fg=COLORS["accent"]).pack(anchor="w")
        tk.Label(info, text=data["username"], font=("Segoe UI", 10),
                 bg=COLORS["card_bg"], fg=COLORS["text_sub"]).pack(anchor="w")

        pwd_label = tk.Label(info, text="••••••••", font=("Consolas", 12),
                             bg=COLORS["card_bg"], fg="white")
        pwd_label.pack(anchor="w")

        actions = tk.Frame(card, bg=COLORS["card_bg"])
        actions.pack(side="right")

        tk.Button(actions, text="✏️", bd=0, bg=COLORS["card_bg"], fg=COLORS["accent"],
                  command=lambda: self.show_edit_popup(data["service"], data["username"], data["password"]),
                  cursor="hand2").pack(side="left", padx=2)
        tk.Button(actions, text="📋", bd=0, bg=COLORS["card_bg"], fg="white",
                  command=lambda: self.copy_to_clipboard(data["password"]),
                  cursor="hand2").pack(side="left", padx=2)
        tk.Button(actions, text="👁️", bd=0, bg=COLORS["card_bg"], fg="white",
                  command=lambda: pwd_label.config(
                      text=data["password"] if pwd_label.cget("text") == "••••••••" else "••••••••"
                  ), cursor="hand2").pack(side="left", padx=2)
        tk.Button(actions, text="🗑️", bd=0, bg=COLORS["card_bg"], fg=COLORS["danger"],
                  command=lambda: self.delete_password(data["service"]),
                  cursor="hand2").pack(side="left", padx=5)

    # ------------------------------------------------
    # ------------------- ADD PASSWORD ---------------
    # ------------------------------------------------
    def render_add_form(self):
        container = tk.Frame(self.content_area, bg=COLORS["bg_dark"])
        container.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(container, text="Ajouter un compte", font=("Segoe UI", 20, "bold"),
                 bg=COLORS["bg_dark"], fg=COLORS["text_main"]).pack(pady=20)

        self.create_entry(container, "Service", "add_service")
        self.create_entry(container, "Identifiant", "add_user")
        self.create_entry(container, "Mot de passe", "add_pass", show="●")

        ModernButton(container, text="ENREGISTRER", width=20, command=self.perform_add).pack(pady=20)

    def perform_add(self):
        srv = self.add_service_entry.get()
        usr = self.add_user_entry.get()
        pwd = self.add_pass_entry.get()

        if not srv or not usr or not pwd:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return

        ok, msg = self.backend.add_password(srv, usr, pwd)
        if ok:
            messagebox.showinfo("Succès", msg)
            self.switch_page("dashboard")
        else:
            messagebox.showerror("Erreur", msg)

    # ------------------------------------------------
    # ------------------- EDIT POPUP -----------------
    # ------------------------------------------------
    def show_edit_popup(self, service, old_user, old_pwd):
        popup = tk.Toplevel(self.root)
        popup.title(f"Modifier {service}")
        popup.configure(bg=COLORS["bg_dark"])
        popup.geometry("400x300")
        popup.grab_set()

        tk.Label(popup, text=f"Modifier {service}", font=("Segoe UI", 16, "bold"),
                 bg=COLORS["bg_dark"], fg=COLORS["accent"]).pack(pady=15)

        new_user = self.create_popup_entry(popup, f"Nouvel identifiant (actuel: {old_user})")
        new_pwd = self.create_popup_entry(popup, "Nouveau mot de passe", show="●")

        ModernButton(popup, text="SAUVEGARDER",
                     command=lambda: self.perform_edit_password(popup, service, new_user.get(), new_pwd.get())).pack(pady=20)

    def create_popup_entry(self, parent, text, show=""):
        tk.Label(parent, text=text, bg=COLORS["bg_dark"], fg=COLORS["text_sub"]).pack(anchor="w", padx=20)
        entry = tk.Entry(parent, show=show, bg=COLORS["input_bg"], fg=COLORS["text_main"], relief="flat", insertbackground="white", width=35)
        entry.pack(ipady=5, padx=20)
        return entry

    def perform_edit_password(self, popup, service, new_u, new_p):
        if not new_u and not new_p:
            messagebox.showerror("Erreur", "Aucun champ modifié.")
            return
        ok, msg = self.backend.modify_password(service, new_u, new_p)
        if ok:
            messagebox.showinfo("Succès", msg)
            popup.destroy()
            self.switch_page("dashboard")
        else:
            messagebox.showerror("Erreur", msg)

    # ------------------------------------------------
    # ------------------- GENERATEUR -----------------
    # ------------------------------------------------
    def render_generator(self):
        container = tk.Frame(self.content_area, bg=COLORS["bg_dark"])
        container.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(container, text="Générateur de mot de passe", font=("Segoe UI", 20, "bold"),
                 bg=COLORS["bg_dark"], fg=COLORS["text_main"]).pack(pady=20)

        self.gen_pwd_var = tk.StringVar(value="Cliquez pour générer")

        tk.Entry(container, textvariable=self.gen_pwd_var, justify="center",
                 font=("Consolas", 16), bg=COLORS["input_bg"], fg=COLORS["accent"],
                 relief="flat", width=25).pack(ipady=10, pady=15)

        btns = tk.Frame(container, bg=COLORS["bg_dark"])
        btns.pack()

        ModernButton(btns, text="GÉNÉRER", command=self.generate_password).pack(side="left", padx=5)
        ModernButton(btns, text="COPIER", bg=COLORS["success"],
                     command=lambda: self.copy_to_clipboard(self.gen_pwd_var.get())).pack(side="left", padx=5)

    def generate_password(self, length=16):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        self.gen_pwd_var.set("".join(secrets.choice(alphabet) for _ in range(length)))

    # ------------------------------------------------
    # ------------------- SETTINGS -------------------
    # ------------------------------------------------
    def render_settings(self):
        container = tk.Frame(self.content_area, bg=COLORS["bg_dark"])
        container.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(container, text="Paramètres du compte", font=("Segoe UI", 20, "bold"),
                 bg=COLORS["bg_dark"], fg=COLORS["text_main"]).pack(anchor="w", pady=10)

        frame_edit = tk.LabelFrame(container, text="Modifier mes informations",
                                   bg=COLORS["bg_dark"], fg=COLORS["accent"])
        frame_edit.pack(fill="x", pady=20)

        inner = tk.Frame(frame_edit, bg=COLORS["bg_dark"])
        inner.pack(fill="x", padx=20, pady=10)

        self.create_entry(inner, "Nouveau nom d'utilisateur", "edit_user")
        self.create_entry(inner, "Nouveau mot de passe maître", "edit_pass", show="●")

        ModernButton(inner, text="METTRE À JOUR", command=self.perform_update_account).pack(pady=10)

        frame_del = tk.LabelFrame(container, text="Zone de Danger",
                                  bg=COLORS["bg_dark"], fg=COLORS["danger"])
        frame_del.pack(fill="x", pady=20)

        inner_d = tk.Frame(frame_del, bg=COLORS["bg_dark"])
        inner_d.pack(fill="x", padx=20, pady=10)

        tk.Label(inner_d, text="Supprimer définitivement votre compte.",
                 bg=COLORS["bg_dark"], fg=COLORS["text_sub"]).pack()

        tk.Button(inner_d, text="SUPPRIMER MON COMPTE", bg=COLORS["danger"],
                  fg="white", relief="flat", cursor="hand2",
                  command=self.perform_delete_account).pack(pady=10)

    def perform_update_account(self):
        new_u = self.edit_user_entry.get()
        new_p = self.edit_pass_entry.get()

        if not new_u and not new_p:
            messagebox.showerror("Erreur", "Aucun changement demandé.")
            return

        confirm = messagebox.askyesno("Confirmer", "Modifier votre compte ?")
        if not confirm:
            return

        ok, msg = self.backend.modify_user_account(new_u, new_p)
        if ok:
            messagebox.showinfo("Succès", "Informations mises à jour. Vous devez vous reconnecter.")
            self.logout()
        else:
            messagebox.showerror("Erreur", msg)

    # ------------------------------------------------
    # ------------------- UTILITAIRES ----------------
    # ------------------------------------------------
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copié", "Mot de passe copié!")

    def delete_password(self, service):
        if messagebox.askyesno("Confirmer", f"Supprimer '{service}' ?"):
            ok, msg = self.backend.delete_password(service)
            if ok:
                self.switch_page("dashboard")
            else:
                messagebox.showerror("Erreur", msg)

    def perform_delete_account(self):
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer votre compte ?"):
            if self.backend.delete_current_account():
                messagebox.showinfo("Compte supprimé", "Votre compte a été supprimé.")
                self.show_login_screen()
            else:
                messagebox.showerror("Erreur", "Échec de la suppression du compte.")

    def logout(self):
        self.backend.logout()
        self.show_login_screen()



