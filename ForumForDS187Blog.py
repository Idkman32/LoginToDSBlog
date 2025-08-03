import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import json
import os
import threading
import ctypes
import random
import time
import pythoncom
import win32com.client
import webbrowser

# Win32 constants
SPI_SETDESKWALLPAPER = 20
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
VK_LWIN = 0x5B

class UserInfoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Uygulama İngilizce başlasın
        self.languages = {'TR': 'Türkçe', 'EN': 'English'}
        self.current_lang = tk.StringVar(value='EN')
        self.texts = {
            'TR': {
                'title': "Kullanıcı Bilgi Formu",
                'name': "Ad:", 'surname': "Soyad:", 'age': "Yaş:",
                'hobbies': "Hobiler:", 'food': "En Sevdiğin Yemek:",
                'free': "Boş Zamanında Ne Yaparsın?:", 'phobias': "Fobilerin:",
                'submit': "Gönder", 'info_title': "Bilgi",
                'info_msg': "O BİLGİLERE İHTİYACIM YOK",
                'ip_label': "IP Bilginiz", 'end_msg': "SEN BİTTİN",
                'shutdown_notice': "Bilgisayar 15 saniye içinde kapanacak..."
            },
            'EN': {
                'title': "User Info Form",
                'name': "Name:", 'surname': "Surname:", 'age': "Age:",
                'hobbies': "Hobbies:", 'food': "Favorite Food:",
                'free': "What do you do in free time?:", 'phobias': "Phobias:",
                'submit': "Submit", 'info_title': "Info",
                'info_msg': "I DON'T NEED THAT INFO",
                'ip_label': "Your IP", 'end_msg': "YOU'RE DONE",
                'shutdown_notice': "Computer will shut down in 15 seconds..."
            }
        }
        self.title(self.texts['EN']['title'])
        self.geometry("700x800")
        self.resizable(True, False)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12))
        style.configure('TButton', font=('Helvetica', 12, 'bold'), padding=6)
        self.create_widgets()

    def create_widgets(self):
        padding = {'padx': 15, 'pady': 8}
        # Dil seçimi
        lang_frame = ttk.Frame(self)
        lang_frame.pack(fill='x', pady=10)
        ttk.Label(lang_frame, text="Dil / Language:").pack(side='left', padx=10)
        self.lang_combo = ttk.Combobox(lang_frame, values=list(self.languages.values()), state='readonly')
        self.lang_combo.pack(side='left')
        self.lang_combo.current(1)
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        # Form alanları
        self.form_frame = ttk.Frame(self, padding=20)
        self.form_frame.pack(fill='both', expand=True)
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=3)
        self.entries = {}
        fields = ['name','surname','age','hobbies','food','free','phobias']
        for idx, field in enumerate(fields):
            lbl = ttk.Label(self.form_frame, text='')
            lbl.grid(row=idx, column=0, sticky='nw' if field in ['hobbies','free','phobias'] else 'w', **padding)
            if field in ['hobbies','free','phobias']:
                txt = tk.Text(self.form_frame, width=40, height=4, font=('Helvetica', 12))
                txt.grid(row=idx, column=1, sticky='ew', **padding)
                self.entries[field] = txt
            else:
                var = tk.StringVar() if field in ['name','surname','food'] else tk.IntVar(value=18)
                widget = ttk.Entry(self.form_frame, textvariable=var) if field in ['name','surname','food'] else ttk.Spinbox(self.form_frame, from_=1, to=120, textvariable=var, width=7)
                widget.grid(row=idx, column=1, sticky='ew', **padding)
                self.entries[field] = var
            self.entries[f"{field}_label"] = lbl
        self.submit_btn = ttk.Button(self, text='', command=self.on_submit)
        self.submit_btn.pack(pady=20)
        self.apply_texts()

    def apply_texts(self):
        lang = self.current_lang.get()
        t = self.texts[lang]
        self.title(t['title'])
        for key in ['name','surname','age','hobbies','food','free','phobias']:
            self.entries[f"{key}_label"].config(text=t[key])
        self.submit_btn.config(text=t['submit'])

    def on_language_change(self, event):
        for code, name in self.languages.items():
            if name == self.lang_combo.get():
                self.current_lang.set(code)
        self.apply_texts()

    def on_submit(self):
        lang = self.current_lang.get()
        t = self.texts[lang]
        # IP ve konum bilgisi
        ip, loc = 'N/A', 'N/A'
        try:
            with urllib.request.urlopen('https://api.ipify.org') as r:
                ip = r.read().decode()
            with urllib.request.urlopen(f'http://ip-api.com/json/{ip}') as r:
                data = json.load(r)
                loc = f"{data.get('city','')} {data.get('regionName','')}"
        except:
            pass
        msg = f"{t['info_msg']}\n\n{t['ip_label']}: {ip}\n{loc} {t['end_msg']}\n\n{t['shutdown_notice']}"
        messagebox.showinfo(title=t['info_title'], message=msg)
        # 15 saniye sonra kapatma komutu başlasın
        threading.Timer(15, lambda: os.system('shutdown /s /t 0')).start()

if __name__ == '__main__':
    pythoncom.CoInitialize()
    app = UserInfoApp()
    app.mainloop()
