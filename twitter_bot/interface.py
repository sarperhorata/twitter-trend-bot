import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from dotenv import load_dotenv

class BotConfigInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Bot Configuration")
        
        # Ana frame'e padding ekle
        self.main_frame = ttk.Frame(root, padding="20")  # padding 10'dan 20'ye çıkarıldı
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Root window'un grid ayarlarını yap
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        
        # Window boyutunu ayarla
        root.geometry("650x600")  # Genişliği biraz artırdık
        
        # Minimum pencere boyutu
        root.minsize(600, 600)
        
        # Mevcut değerleri yükle
        self.load_existing_config()
        
        # Hesap bilgileri için frame'ler
        self.create_account_frames()
        
        # Bot ayarları
        self.create_bot_settings()
        
        # Butonlar
        self.create_buttons()

    def load_existing_config(self):
        """Mevcut .env dosyasından değerleri yükle"""
        load_dotenv()
        self.existing_config = {
            'TWITTER1_BEARER_TOKEN': os.getenv('TWITTER1_BEARER_TOKEN', ''),
            'TWITTER1_API_KEY': os.getenv('TWITTER1_API_KEY', ''),
            'TWITTER1_API_SECRET': os.getenv('TWITTER1_API_SECRET', ''),
            'TWITTER1_ACCESS_TOKEN': os.getenv('TWITTER1_ACCESS_TOKEN', ''),
            'TWITTER1_ACCESS_TOKEN_SECRET': os.getenv('TWITTER1_ACCESS_TOKEN_SECRET', ''),
            
            'TWITTER2_BEARER_TOKEN': os.getenv('TWITTER2_BEARER_TOKEN', ''),
            'TWITTER2_API_KEY': os.getenv('TWITTER2_API_KEY', ''),
            'TWITTER2_API_SECRET': os.getenv('TWITTER2_API_SECRET', ''),
            'TWITTER2_ACCESS_TOKEN': os.getenv('TWITTER2_ACCESS_TOKEN', ''),
            'TWITTER2_ACCESS_TOKEN_SECRET': os.getenv('TWITTER2_ACCESS_TOKEN_SECRET', ''),
            
            'BOT_NAME': os.getenv('BOT_NAME', '@TrendAnalyzerBot'),
            'BOT_PERSONALITY': os.getenv('BOT_PERSONALITY', 'Witty and sarcastic'),
            'BOT_LANGUAGE': os.getenv('BOT_LANGUAGE', 'English'),
            'CHECK_INTERVAL': os.getenv('CHECK_INTERVAL', '12'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', '')
        }

    def create_account_frames(self):
        for i in range(2):
            account_frame = ttk.LabelFrame(self.main_frame, text=f"Account {i+1}")
            account_frame.grid(row=i, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W+tk.E)
            
            fields = ['Bearer Token', 'API Key', 'API Secret', 
                     'Access Token', 'Access Token Secret']
            
            for j, field in enumerate(fields):
                ttk.Label(account_frame, text=field).grid(row=j, column=0, padx=5, pady=2)
                entry = ttk.Entry(account_frame, width=50)
                entry.grid(row=j, column=1, padx=5, pady=2)
                
                # Sağ tık menüsü ekle
                self.add_right_click_menu(entry)
                
                # Mevcut değeri yükle
                config_key = f'TWITTER{i+1}_{field.upper().replace(" ", "_")}'
                if config_key in self.existing_config:
                    entry.insert(0, self.existing_config[config_key])
                
                setattr(self, f'account{i+1}_{field.lower().replace(" ", "_")}', entry)

        # OpenAI API Key frame
        openai_frame = ttk.LabelFrame(self.main_frame, text="OpenAI Settings")
        openai_frame.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W+tk.E)
        
        ttk.Label(openai_frame, text="API Key").grid(row=0, column=0, padx=5, pady=2)
        self.openai_api_key = ttk.Entry(openai_frame, width=50)
        self.openai_api_key.grid(row=0, column=1, padx=5, pady=2)
        self.add_right_click_menu(self.openai_api_key)
        
        if 'OPENAI_API_KEY' in self.existing_config:
            self.openai_api_key.insert(0, self.existing_config['OPENAI_API_KEY'])

    def create_bot_settings(self):
        bot_frame = ttk.LabelFrame(self.main_frame, text="Bot Settings")
        bot_frame.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W+tk.E)
        
        # Bot Name (Default değer ile)
        ttk.Label(bot_frame, text="Bot Name").grid(row=0, column=0, padx=5, pady=2)
        self.bot_bot_name = ttk.Entry(bot_frame, width=50)
        self.bot_bot_name.insert(0, "@TrendAnalyzerBot")
        self.bot_bot_name.grid(row=0, column=1, padx=5, pady=2)
        
        # Bot Personality (Dropdown)
        ttk.Label(bot_frame, text="Bot Personality").grid(row=1, column=0, padx=5, pady=2)
        personalities = [
            "Witty and sarcastic",
            "Professional and analytical",
            "Friendly and helpful",
            "Humorous and playful",
            "Intellectual and philosophical",
            "Tech-savvy and geeky"
        ]
        self.bot_bot_personality = ttk.Combobox(bot_frame, values=personalities, state='readonly', width=47)
        self.bot_bot_personality.set(personalities[0])
        self.bot_bot_personality.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Bot Language (Dropdown)
        ttk.Label(bot_frame, text="Bot Language").grid(row=2, column=0, padx=5, pady=2)
        self.bot_bot_language = ttk.Combobox(bot_frame, values=['English'], state='readonly', width=47)
        self.bot_bot_language.set('English')
        self.bot_bot_language.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Check Interval (Dropdown)
        ttk.Label(bot_frame, text="Check Interval (hours)").grid(row=3, column=0, padx=5, pady=2)
        self.bot_check_interval = ttk.Combobox(bot_frame, values=['3', '6', '9', '12', '24', '48'], state='readonly', width=47)
        self.bot_check_interval.set('12')
        self.bot_check_interval.grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)

    def add_right_click_menu(self, entry):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Cut", command=lambda: entry.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: entry.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: entry.event_generate("<<Paste>>"))
        
        entry.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))
        entry.bind("<Control-v>", lambda e: entry.event_generate("<<Paste>>"))
        entry.bind("<Control-c>", lambda e: entry.event_generate("<<Copy>>"))
        entry.bind("<Control-x>", lambda e: entry.event_generate("<<Cut>>"))

    def create_buttons(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Config butonları
        config_buttons = ttk.Frame(button_frame)
        config_buttons.grid(row=0, column=0, pady=5)
        ttk.Button(config_buttons, text="Save", command=self.save_config, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(config_buttons, text="Clear All", command=self.clear_all, width=15).grid(row=0, column=1, padx=5)
        
        # Bot kontrol butonları
        control_buttons = ttk.Frame(button_frame)
        control_buttons.grid(row=1, column=0, pady=5)
        ttk.Button(control_buttons, text="Start Bot", command=self.start_bot, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(control_buttons, text="Stop Bot", command=self.stop_bot, width=15).grid(row=0, column=1, padx=5)

    def clear_all(self):
        """Tüm alanları temizle"""
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Entry):
                        child.delete(0, tk.END)

    def start_bot(self):
        try:
            os.system('python -m twitter_bot.main &')
            messagebox.showinfo("Success", "Bot started successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start bot: {str(e)}")

    def stop_bot(self):
        try:
            os.system('pkill -f "python -m twitter_bot.main"')
            messagebox.showinfo("Success", "Bot stopped successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop bot: {str(e)}")

    def save_config(self):
        try:
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
                'CHECK_INTERVAL': self.bot_check_interval.get(),
                'OPENAI_API_KEY': self.openai_api_key.get()
            }
            
            # Mevcut .env dosyasından diğer değerleri koru
            load_dotenv()
            existing_config = {
                key: os.getenv(key)
                for key in ['ADMIN_USERNAME', 'ADMIN_PASSWORD_HASH', 'SECRET_KEY', 'FLASK_ENV']
                if os.getenv(key)
            }
            
            config.update(existing_config)
            
            # .env dosyasını güncelle
            with open('.env', 'w') as f:
                for key, value in config.items():
                    f.write(f'{key}={value}\n')
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
            self.root.destroy()
        except Exception as e:
            print(f"Error while saving: {str(e)}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

def run_interface():
    root = tk.Tk()
    app = BotConfigInterface(root)
    root.mainloop()

if __name__ == "__main__":
    run_interface() 