import tkinter as tk
from tkinter import ttk
import json
import os

class BotConfigInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Bot Configuration")
        
        # Ana frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Hesap bilgileri için frame'ler
        self.create_account_frames()
        
        # Bot ayarları
        self.create_bot_settings()
        
        # Kaydet butonu
        ttk.Button(self.main_frame, text="Save", command=self.save_config).grid(
            row=4, column=0, columnspan=2, pady=10)

    def create_account_frames(self):
        for i in range(2):
            account_frame = ttk.LabelFrame(self.main_frame, text=f"Account {i+1}")
            account_frame.grid(row=i, column=0, columnspan=2, pady=5, sticky=tk.W+tk.E)
            
            fields = ['Bearer Token', 'API Key', 'API Secret', 
                     'Access Token', 'Access Token Secret']
            
            for j, field in enumerate(fields):
                ttk.Label(account_frame, text=field).grid(row=j, column=0, padx=5, pady=2)
                entry = ttk.Entry(account_frame, width=50)
                entry.grid(row=j, column=1, padx=5, pady=2)
                setattr(self, f'account{i+1}_{field.lower().replace(" ", "_")}', entry)

    def create_bot_settings(self):
        bot_frame = ttk.LabelFrame(self.main_frame, text="Bot Settings")
        bot_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.W+tk.E)
        
        fields = ['Bot Name', 'Bot Personality', 'Bot Language', 'Check Interval (hours)']
        
        for i, field in enumerate(fields):
            ttk.Label(bot_frame, text=field).grid(row=i, column=0, padx=5, pady=2)
            entry = ttk.Entry(bot_frame, width=50)
            entry.grid(row=i, column=1, padx=5, pady=2)
            setattr(self, f'bot_{field.lower().replace(" ", "_")}', entry)

    def save_config(self):
        config = {
            'TWITTER1_BEARER_TOKEN': self.account1_bearer_token.get(),
            'TWITTER1_API_KEY': self.account1_api_key.get(),
            'TWITTER1_API_SECRET': self.account1_api_secret.get(),
            'TWITTER1_ACCESS_TOKEN': self.account1_access_token.get(),
            'TWITTER1_ACCESS_TOKEN_SECRET': self.account1_access_token_secret.get(),
            
            'TWITTER2_BEARER_TOKEN': self.account2_bearer_token.get(),
            'TWITTER2_API_KEY': self.account2_api_key.get(),
            'TWITTER2_API_SECRET': self.account2_api_secret.get(),
            'TWITTER2_ACCESS_TOKEN': self.account2_access_token.get(),
            'TWITTER2_ACCESS_TOKEN_SECRET': self.account2_access_token_secret.get(),
            
            'BOT_NAME': self.bot_bot_name.get(),
            'BOT_PERSONALITY': self.bot_bot_personality.get(),
            'BOT_LANGUAGE': self.bot_bot_language.get(),
            'CHECK_INTERVAL': self.bot_check_interval_hours.get(),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', '')
        }
        
        # .env dosyasını oluştur
        with open('.env', 'w') as f:
            for key, value in config.items():
                f.write(f'{key}={value}\n')
        
        self.root.destroy()

def run_interface():
    root = tk.Tk()
    app = BotConfigInterface(root)
    root.mainloop()

if __name__ == "__main__":
    run_interface() 