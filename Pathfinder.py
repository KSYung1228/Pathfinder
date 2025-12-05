import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import paramiko
import threading
import os
import json
import base64

# --- 設定檔管理 (Config Manager) ---
CONFIG_FILE = "sftp_config.json"

class ConfigManager:
    @staticmethod
    def load_config():
        if not os.path.exists(CONFIG_FILE):
            return {}
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    @staticmethod
    def save_config(data):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    @staticmethod
    def encode_password(pwd):
        # 簡單的 Base64 編碼 (僅為了不讓 json 直接顯示明文，非高強度加密)
        return base64.b64encode(pwd.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decode_password(encoded_pwd):
        try:
            return base64.b64decode(encoded_pwd.encode("utf-8")).decode("utf-8")
        except:
            return ""

# --- 語言字典 ---
LANG_TEXT = {
    "zh": {
        "title": "Pathfinder",
        "grp_profile": "快速連線 / 歷史紀錄",
        "lbl_profile": "選擇設定檔:",
        "btn_delete": "刪除設定",
        "chk_save": "記住此連線資訊",
        "grp_conn": "連線資訊",
        "lbl_host": "主機 IP:",
        "lbl_port": "Port:",
        "lbl_user": "使用者帳號:",
        "lbl_pass": "密碼:",
        "grp_search": "搜尋設定",
        "lbl_path": "起始路徑:",
        "lbl_keyword": "關鍵字:",
        "lbl_mode": "搜尋模式:",
        "rb_filename": "搜尋檔名",
        "rb_content": "搜尋內容 (Grep)",
        "btn_start": "開始搜尋",
        "btn_searching": "搜尋進行中...",
        "btn_clear": "清除紀錄",
        "btn_lang": "English",
        "err_fields": "❌ 錯誤: 請填寫所有必填欄位。",
        "log_conn": "連線至 {}...",
        "log_success": "✅ 連線成功！正在執行指令...",
        "log_found": "🎉 找到 {} 個結果：",
        "log_nofound": "🔍 在 {} 下找不到關鍵字 '{}'",
        "log_file": "📄 檔案",
        "log_folder": "📂 目錄",
        "err_auth": "❌ 認證失敗，請檢查帳號密碼。",
        "err_ssh": "❌ SSH 錯誤: {}",
        "err_gen": "❌ 發生錯誤: {}",
        "tip_content": "⚠️ 注意：內容搜尋會讀取檔案，速度較慢，請稍候...",
        "msg_saved": "設定已儲存",
        "msg_deleted": "設定已刪除"
    },
    "en": {
        "title": "Pathfinder",
        "grp_profile": "Quick Connect / History",
        "lbl_profile": "Select Profile:",
        "btn_delete": "Delete Profile",
        "chk_save": "Save Connection Info",
        "grp_conn": "Connection Info",
        "lbl_host": "Host IP:",
        "lbl_port": "Port:",
        "lbl_user": "Username:",
        "lbl_pass": "Password:",
        "grp_search": "Search Criteria",
        "lbl_path": "Start Path:",
        "lbl_keyword": "Keyword:",
        "lbl_mode": "Mode:",
        "rb_filename": "Filename",
        "rb_content": "File Content",
        "btn_start": "Search",
        "btn_searching": "Searching...",
        "btn_clear": "Clear Log",
        "btn_lang": "中文",
        "err_fields": "❌ Error: All fields are required.",
        "log_conn": "Connecting to {}...",
        "log_success": "✅ Connected! Executing command...",
        "log_found": "🎉 Found {} results:",
        "log_nofound": "🔍 No results found for '{}' in {}",
        "log_file": "📄 File",
        "log_folder": "📂 Folder",
        "err_auth": "❌ Auth failed.",
        "err_ssh": "❌ SSH Error: {}",
        "err_gen": "❌ Error: {}",
        "tip_content": "⚠️ Note: Content search reads files and may be slow.",
        "msg_saved": "Config Saved",
        "msg_deleted": "Config Deleted"
    }
}

class SFTPFinderApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "zh"
        
        # 載入設定檔
        self.saved_profiles = ConfigManager.load_config()
        
        # 1. 視窗設定
        self.window_width = 750
        self.window_height = 720
        self.center_window()
        self.root.configure(bg="#f3f3f3") # Win11 淺灰色背景
        
        # 2. 樣式
        self.setup_style()
        
        # 變數
        self.search_mode = tk.StringVar(value="filename")
        self.save_conn_var = tk.BooleanVar(value=True) # 預設勾選儲存
        self.selected_profile = tk.StringVar()

        # 建構介面
        self.setup_ui()
        self.update_language()
        
        # 初始載入設定檔列表
        self.update_profile_list()

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (self.window_width / 2))
        y_cordinate = int((screen_height / 2) - (self.window_height / 2))
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x_cordinate}+{y_cordinate}")

    def setup_style(self):
        style = ttk.Style()
        
        # 嘗試使用 Windows 原生主題
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
            
        # 字體設定 (使用 Win11 常用的 Segoe UI)
        default_font = ("Segoe UI", 10)
        bold_font = ("Segoe UI", 10, "bold")
        header_font = ("Segoe UI Variable Display", 14, "bold")
        
        style.configure(".", font=default_font, background="#f3f3f3")
        
        # LabelFrame 樣式
        style.configure("TLabelframe", background="#f3f3f3", borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", font=bold_font, foreground="#0067c0", background="#f3f3f3")
        
        # Label 樣式
        style.configure("TLabel", background="#f3f3f3", foreground="#333333")
        style.configure("Header.TLabel", font=header_font, foreground="#1a1a1a", background="#f3f3f3")
        
        # Entry 樣式 (稍微加高一點看起來比較現代)
        style.configure("TEntry", padding=5)
        
        # Button 樣式
        style.configure("TButton", font=default_font, padding=6)
        # 只有在 clam 主題下這些顏色設定才比較明顯，vista 主題受限於系統繪製
        style.map("TButton",
                  foreground=[('pressed', 'black'), ('active', 'black')],
                  background=[('pressed', '!disabled', '#ccc'), ('active', '#eaeaea')])

        # Checkbutton
        style.configure("TCheckbutton", background="#f3f3f3")

    def setup_ui(self):
        # 主容器 (白色卡片風格)
        main_container = tk.Frame(self.root, bg="#f3f3f3")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 頂部標題列
        top_frame = tk.Frame(main_container, bg="#f3f3f3")
        top_frame.pack(fill="x", pady=(0, 20))
        
        self.lbl_title = ttk.Label(top_frame, text="SFTP Finder", style="Header.TLabel")
        self.lbl_title.pack(side="left")
        
        self.btn_lang = ttk.Button(top_frame, command=self.toggle_language, width=10)
        self.btn_lang.pack(side="right")

        # --- 0. 設定檔選擇區 (新增) ---
        self.profile_frame = ttk.LabelFrame(main_container, padding="15 15")
        self.profile_frame.pack(fill="x", pady=(0, 15))
        self.profile_frame.columnconfigure(1, weight=1)

        self.lbl_profile = ttk.Label(self.profile_frame)
        self.lbl_profile.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.combo_profile = ttk.Combobox(self.profile_frame, textvariable=self.selected_profile, state="readonly")
        self.combo_profile.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.combo_profile.bind("<<ComboboxSelected>>", self.on_profile_select)

        self.btn_delete_profile = ttk.Button(self.profile_frame, command=self.delete_profile)
        self.btn_delete_profile.grid(row=0, column=2, sticky="e")

        # --- 1. 連線區塊 ---
        self.conn_frame = ttk.LabelFrame(main_container, padding="15 15")
        self.conn_frame.pack(fill="x", pady=(0, 15))
        self.conn_frame.columnconfigure(1, weight=1)
        self.conn_frame.columnconfigure(3, weight=1)

        # Row 0
        self.lbl_host = ttk.Label(self.conn_frame)
        self.lbl_host.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.entry_host = ttk.Entry(self.conn_frame)
        self.entry_host.grid(row=0, column=1, sticky="ew", padx=(0, 15))

        self.lbl_port = ttk.Label(self.conn_frame)
        self.lbl_port.grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.entry_port = ttk.Entry(self.conn_frame, width=6)
        self.entry_port.insert(0, "22")
        self.entry_port.grid(row=0, column=3, sticky="w")

        # Row 1
        self.lbl_user = ttk.Label(self.conn_frame)
        self.lbl_user.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(15, 0))
        self.entry_user = ttk.Entry(self.conn_frame)
        self.entry_user.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=(15, 0))

        self.lbl_pass = ttk.Label(self.conn_frame)
        self.lbl_pass.grid(row=1, column=2, sticky="w", padx=(0, 5), pady=(15, 0))
        self.entry_pass = ttk.Entry(self.conn_frame, show="*")
        self.entry_pass.grid(row=1, column=3, sticky="ew", pady=(15, 0))
        
        # Row 2 (儲存選項)
        self.chk_save = ttk.Checkbutton(self.conn_frame, variable=self.save_conn_var)
        self.chk_save.grid(row=2, column=0, columnspan=4, sticky="w", pady=(15, 0))

        # --- 2. 搜尋區塊 ---
        self.search_frame = ttk.LabelFrame(main_container, padding="15 15")
        self.search_frame.pack(fill="x", pady=(0, 15))
        self.search_frame.columnconfigure(1, weight=1)

        # Path
        self.lbl_path = ttk.Label(self.search_frame)
        self.lbl_path.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.entry_path = ttk.Entry(self.search_frame)
        self.entry_path.insert(0, ".")
        self.entry_path.grid(row=0, column=1, sticky="ew")

        # Keyword
        self.lbl_keyword = ttk.Label(self.search_frame)
        self.lbl_keyword.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(15, 0))
        self.entry_keyword = ttk.Entry(self.search_frame)
        self.entry_keyword.grid(row=1, column=1, sticky="ew", pady=(15, 0))

        # Mode
        self.lbl_mode = ttk.Label(self.search_frame)
        self.lbl_mode.grid(row=2, column=0, sticky="w", padx=(0, 5), pady=(15, 0))
        
        mode_panel = ttk.Frame(self.search_frame)
        mode_panel.grid(row=2, column=1, sticky="w", pady=(15, 0))
        
        self.rb_filename = ttk.Radiobutton(mode_panel, variable=self.search_mode, value="filename")
        self.rb_filename.pack(side="left", padx=(0, 15))
        
        self.rb_content = ttk.Radiobutton(mode_panel, variable=self.search_mode, value="content")
        self.rb_content.pack(side="left")

        # --- 3. 按鈕區 ---
        btn_frame = ttk.Frame(main_container)
        btn_frame.pack(fill="x", pady=(0, 15))
        
        # 強調色按鈕 (搜尋)
        self.btn_search = ttk.Button(btn_frame, command=self.start_search_thread)
        self.btn_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_clear = ttk.Button(btn_frame, command=self.clear_log)
        self.btn_clear.pack(side="right")

        # --- 4. 日誌區 (圓角與陰影較難實現，使用邊框模擬) ---
        log_frame = tk.Frame(main_container, bg="#ddd", bd=1)
        log_frame.pack(fill="both", expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', 
                                                  font=("Consolas", 9), 
                                                  bg="#ffffff", fg="#333", relief="flat", padx=10, pady=10)
        self.log_area.pack(fill="both", expand=True, padx=1, pady=1)

    # --- 功能邏輯 ---

    def update_profile_list(self):
        """更新下拉選單內容"""
        profiles = list(self.saved_profiles.keys())
        self.combo_profile['values'] = profiles
        if profiles:
            self.combo_profile.current(0)
            self.on_profile_select(None)

    def on_profile_select(self, event):
        """當使用者選擇設定檔時，填入對應欄位"""
        name = self.selected_profile.get()
        if name in self.saved_profiles:
            data = self.saved_profiles[name]
            self.entry_host.delete(0, tk.END)
            self.entry_host.insert(0, data.get("host", ""))
            
            self.entry_port.delete(0, tk.END)
            self.entry_port.insert(0, str(data.get("port", "22")))
            
            self.entry_user.delete(0, tk.END)
            self.entry_user.insert(0, data.get("user", ""))
            
            self.entry_pass.delete(0, tk.END)
            self.entry_pass.insert(0, ConfigManager.decode_password(data.get("password", "")))

    def delete_profile(self):
        name = self.selected_profile.get()
        if name and name in self.saved_profiles:
            del self.saved_profiles[name]
            ConfigManager.save_config(self.saved_profiles)
            self.update_profile_list()
            
            # 清空欄位
            self.entry_host.delete(0, tk.END)
            self.entry_port.delete(0, tk.END)
            self.entry_port.insert(0, "22")
            self.entry_user.delete(0, tk.END)
            self.entry_pass.delete(0, tk.END)
            self.combo_profile.set('')
            
            t = LANG_TEXT[self.current_lang]
            self.log(f"[{t['msg_deleted']}: {name}]", "#e74c3c")

    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "zh" else "zh"
        self.update_language()

    def update_language(self):
        t = LANG_TEXT[self.current_lang]
        self.root.title(t["title"])
        self.lbl_title.config(text=t["title"])
        self.btn_lang.config(text=t["btn_lang"])
        
        self.profile_frame.config(text=t["grp_profile"])
        self.lbl_profile.config(text=t["lbl_profile"])
        self.btn_delete_profile.config(text=t["btn_delete"])
        
        self.conn_frame.config(text=t["grp_conn"])
        self.lbl_host.config(text=t["lbl_host"])
        self.lbl_port.config(text=t["lbl_port"])
        self.lbl_user.config(text=t["lbl_user"])
        self.lbl_pass.config(text=t["lbl_pass"])
        self.chk_save.config(text=t["chk_save"])
        
        self.search_frame.config(text=t["grp_search"])
        self.lbl_path.config(text=t["lbl_path"])
        self.lbl_keyword.config(text=t["lbl_keyword"])
        self.lbl_mode.config(text=t["lbl_mode"])
        self.rb_filename.config(text=t["rb_filename"])
        self.rb_content.config(text=t["rb_content"])
        
        if str(self.btn_search['state']) != 'disabled':
            self.btn_search.config(text=t["btn_start"])
        self.btn_clear.config(text=t["btn_clear"])

    def log(self, message, color="#333333"):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n", ("color",))
        self.log_area.tag_config("color", foreground=color)
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def clear_log(self):
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')

    def start_search_thread(self):
        t = LANG_TEXT[self.current_lang]
        self.btn_search.config(state="disabled", text=t["btn_searching"])
        if self.search_mode.get() == "content":
            self.log(t["tip_content"], "#e67e22")
        
        thread = threading.Thread(target=self.perform_search)
        thread.daemon = True
        thread.start()

    def perform_search(self):
        t = LANG_TEXT[self.current_lang]
        host = self.entry_host.get().strip()
        try:
            port = int(self.entry_port.get().strip())
        except:
            port = 22
        user = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        path = self.entry_path.get().strip()
        keyword = self.entry_keyword.get().strip()
        mode = self.search_mode.get()

        if not host or not user or not password or not keyword:
            self.log(t["err_fields"], "#e74c3c")
            self.reset_button()
            return

        # --- 處理儲存邏輯 ---
        if self.save_conn_var.get():
            profile_name = f"{user}@{host}"
            self.saved_profiles[profile_name] = {
                "host": host,
                "port": port,
                "user": user,
                "password": ConfigManager.encode_password(password)
            }
            ConfigManager.save_config(self.saved_profiles)
            # 在主執行緒更新 UI
            self.root.after(0, self.update_profile_list)
            # 保持當前選擇
            self.root.after(0, lambda: self.combo_profile.set(profile_name))

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.log(t["log_conn"].format(host), "#0067c0")
            ssh.connect(host, port=port, username=user, password=password, timeout=10)
            self.log(t["log_success"], "#107c10")

            if mode == "filename":
                command = f"find {path} -name '*{keyword}*' 2>/dev/null"
            else:
                command = f"grep -rl '{keyword}' {path} 2>/dev/null"

            stdin, stdout, stderr = ssh.exec_command(command)
            
            try:
                results = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
            except Exception as e:
                self.log(f"Decode Error: {e}", "red")
                results = []

            results = [r for r in results if r]

            self.log("-" * 45)
            if results:
                self.log(t["log_found"].format(len(results)), "#107c10")
                for item_path in results:
                    folder = os.path.dirname(item_path)
                    self.log(f"{t['log_file']}: {item_path}", "#2c3e50")
                    self.log(f"{t['log_folder']}: {folder}", "#7f8c8d")
                    self.log("-" * 25)
            else:
                self.log(t["log_nofound"].format(path, keyword), "#e67e22")
            self.log("-" * 45)

            ssh.close()

        except paramiko.AuthenticationException:
            self.log(t["err_auth"], "#c0392b")
        except Exception as e:
            self.log(t["err_gen"].format(e), "#c0392b")
        finally:
            self.reset_button()

    def reset_button(self):
        t = LANG_TEXT[self.current_lang]
        self.root.after(0, lambda: self.btn_search.config(state="normal", text=t["btn_start"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = SFTPFinderApp(root)
    root.mainloop()