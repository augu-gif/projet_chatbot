import tkinter as tk
from tkinter import ttk, scrolledtext, font
from typing import Callable
from ..core.chatbot import LegalAnnouncementChatbot

class ChatbotGUI:
    def __init__(self, chatbot: LegalAnnouncementChatbot):
        """
        Initialise l'interface graphique du chatbot
        
        Args:
            chatbot: Instance du chatbot
        """
        self.chatbot = chatbot
        self.root = tk.Tk()
        self.root.title("Chatbot - La Gazette")
        self.root.geometry("600x500")
        self.root.configure(bg="#E8F1F8")  # Bleu très clair pour le fond
        
        # Configuration des couleurs
        self.colors = {
            "bg": "#E8F1F8",        # Bleu très clair
            "text": "#1A365D",      # Bleu foncé
            "button": "#2B6CB0",    # Bleu moyen
            "button_text": "white",
            "input_bg": "white",
            "chat_bg": "white"
        }
        
        # Configuration des polices
        self.fonts = {
            "title": ("Helvetica", 16, "bold"),
            "chat": ("Helvetica", 10),
            "input": ("Helvetica", 10),
            "button": ("Helvetica", 10, "bold")
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Titre stylisé
        title_label = tk.Label(
            main_frame,
            text="🤖 Chatbot – La Gazette",
            font=self.fonts["title"],
            bg=self.colors["bg"],
            fg=self.colors["text"],
            pady=10
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="we")
        
        # Frame pour la zone de chat avec bordure
        chat_frame = ttk.Frame(main_frame, style="Chat.TFrame")
        chat_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        # Zone de chat avec style personnalisé
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=self.fonts["chat"],
            bg=self.colors["chat_bg"],
            fg=self.colors["text"],
            padx=10,
            pady=10
        )
        self.chat_area.grid(row=0, column=0, sticky="nsew")
        self.chat_area.config(state=tk.DISABLED)
        
        # Frame pour la zone de saisie
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky="we")
        
        # Zone de saisie avec style
        self.input_field = ttk.Entry(
            input_frame,
            font=self.fonts["input"],
            width=40
        )
        self.input_field.grid(row=0, column=0, sticky="we", padx=(0, 10))
        self.input_field.bind("<Return>", self.send_message)
        
        # Style personnalisé pour le bouton
        style = ttk.Style()
        style.configure(
            "Custom.TButton",
            background=self.colors["button"],
            foreground=self.colors["button_text"],
            font=self.fonts["button"],
            padding=5
        )
        
        # Bouton d'envoi stylisé
        send_button = ttk.Button(
            input_frame,
            text="Envoyer",
            command=self.send_message,
            style="Custom.TButton"
        )
        send_button.grid(row=0, column=1, sticky=(tk.E))
        
        # Configuration du redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)
        
        # Message de bienvenue
        self.add_message("Assistant", "Bonjour ! Je suis votre assistant pour les annonces légales. Comment puis-je vous aider ?")
    
    def add_message(self, sender: str, message: str):
        """Ajoute un message à la zone de chat avec style"""
        self.chat_area.config(state=tk.NORMAL)
        
        # Style différent pour l'utilisateur et l'assistant
        if sender == "Vous":
            self.chat_area.insert(tk.END, f"{sender}: ", "user")
            self.chat_area.insert(tk.END, f"{message}\n\n", "user_message")
        else:
            self.chat_area.insert(tk.END, f"{sender}: ", "assistant")
            self.chat_area.insert(tk.END, f"{message}\n\n", "assistant_message")
        
        # Configuration des tags pour le style
        self.chat_area.tag_configure("user", font=self.fonts["chat"], foreground="#2B6CB0")
        self.chat_area.tag_configure("user_message", font=self.fonts["chat"], foreground=self.colors["text"])
        self.chat_area.tag_configure("assistant", font=self.fonts["chat"], foreground="#2C5282")
        self.chat_area.tag_configure("assistant_message", font=self.fonts["chat"], foreground=self.colors["text"])
        
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Envoie le message de l'utilisateur et obtient la réponse du chatbot"""
        message = self.input_field.get().strip()
        if message:
            # Afficher le message de l'utilisateur
            self.add_message("Vous", message)
            
            # Obtenir et afficher la réponse du chatbot
            response = self.chatbot.get_response(message)
            self.add_message("Assistant", response)
            
            # Effacer le champ de saisie
            self.input_field.delete(0, tk.END)
    
    def run(self):
        """Lance l'interface graphique"""
        self.root.mainloop() 