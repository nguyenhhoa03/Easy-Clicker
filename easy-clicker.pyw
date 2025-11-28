import customtkinter as ctk
import json
import socket
import threading
import subprocess
import sys
import os
import pyautogui
import time
from tkinter import filedialog, messagebox

class EasyClicker:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Easy Clicker")
        self.window.geometry("700x600")
        
        self.actions = []
        self.clicker_processes = []
        self.server_socket = None
        self.server_port = 0
        self.is_running = False
        self.stop_flag = False
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
        self.start_server()
        
    def setup_ui(self):
        # Frame chính
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame điều khiển trên cùng
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        # Nút thêm hành động
        ctk.CTkButton(control_frame, text="➕ Click Trái", 
                     command=lambda: self.add_action("left")).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="➕ Click Phải", 
                     command=lambda: self.add_action("right")).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="➕ Nháy Đúp", 
                     command=lambda: self.add_action("double")).pack(side="left", padx=5)
        
        # Nút Load/Save
        ctk.CTkButton(control_frame, text="📁 Load", 
                     command=self.load_config).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="💾 Save", 
                     command=self.save_config).pack(side="left", padx=5)
        
        # Frame danh sách hành động với scrollbar
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.scroll_frame = ctk.CTkScrollableFrame(list_frame, height=300)
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Frame cấu hình lặp lại
        repeat_frame = ctk.CTkFrame(main_frame)
        repeat_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(repeat_frame, text="Lặp lại:").pack(side="left", padx=5)
        
        self.repeat_mode = ctk.StringVar(value="infinite")
        ctk.CTkRadioButton(repeat_frame, text="Vô hạn", variable=self.repeat_mode, 
                          value="infinite").pack(side="left", padx=5)
        ctk.CTkRadioButton(repeat_frame, text="N lần", variable=self.repeat_mode, 
                          value="times").pack(side="left", padx=5)
        ctk.CTkRadioButton(repeat_frame, text="N phút", variable=self.repeat_mode, 
                          value="minutes").pack(side="left", padx=5)
        
        self.repeat_value = ctk.CTkEntry(repeat_frame, width=80, placeholder_text="Số lần/phút")
        self.repeat_value.pack(side="left", padx=5)
        
        # Frame điều khiển chạy
        run_frame = ctk.CTkFrame(main_frame)
        run_frame.pack(fill="x", padx=5, pady=5)
        
        self.start_btn = ctk.CTkButton(run_frame, text="▶️ Bắt Đầu", 
                                       command=self.start_clicking, fg_color="green")
        self.start_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        self.stop_btn = ctk.CTkButton(run_frame, text="⏹️ Dừng", 
                                      command=self.stop_clicking, fg_color="red", state="disabled")
        self.stop_btn.pack(side="left", padx=5, expand=True, fill="x")
        
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', 0))
        self.server_port = self.server_socket.getsockname()[1]
        self.server_socket.listen(10)
        
        thread = threading.Thread(target=self.listen_clickers, daemon=True)
        thread.start()
        
    def listen_clickers(self):
        while True:
            try:
                client, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client,), daemon=True)
                thread.start()
            except:
                break
                
    def handle_client(self, client):
        try:
            data = client.recv(1024).decode()
            if data:
                parts = data.split(":")
                if len(parts) == 3:
                    cmd, idx, pos = parts
                    idx = int(idx)
                    if cmd == "POS" and idx < len(self.actions):
                        self.actions[idx]["position"] = pos
                        self.update_action_display()
        except:
            pass
        finally:
            client.close()
            
    def add_action(self, action_type):
        idx = len(self.actions)
        
        # Lấy script path để gọi clicker.py đúng
        script_dir = os.path.dirname(os.path.abspath(__file__))
        clicker_path = os.path.join(script_dir, "clicker.py")
        
        # Sử dụng pythonw.exe để không hiện cmd
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable
            
        cmd = [python_exe, clicker_path, 
               f"--port={self.server_port}", 
               f"--location={idx}", 
               f"--type={action_type}"]
        
        process = subprocess.Popen(cmd, 
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        
        action = {
            "type": action_type,
            "position": "0x0",
            "duration": 300 if action_type != "double" else 100,
            "delay": 300 if action_type != "double" else 350,
            "process": process
        }
        
        self.actions.append(action)
        self.clicker_processes.append(process)
        self.update_action_display()
        
    def update_action_display(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        for idx, action in enumerate(self.actions):
            self.create_action_widget(idx, action)
            
    def create_action_widget(self, idx, action):
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", padx=5, pady=3)
        
        type_map = {"left": "Click trái", "right": "Click phải", "double": "Nháy đúp"}
        pos = action["position"]
        duration = action["duration"]
        delay = action["delay"]
        
        text = f"{idx+1}: {type_map[action['type']]} tại {pos} trong {duration}ms\nDelay {delay}ms"
        
        label = ctk.CTkLabel(frame, text=text, width=400, anchor="w")
        label.pack(side="left", padx=5)
        
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(side="right", padx=5)
        
        ctk.CTkButton(btn_frame, text="⚙️", width=40, 
                     command=lambda i=idx: self.edit_action(i)).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="🔼", width=40, 
                     command=lambda i=idx: self.move_action(i, -1)).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="🔽", width=40, 
                     command=lambda i=idx: self.move_action(i, 1)).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="❌", width=40, 
                     command=lambda i=idx: self.delete_action(i)).pack(side="left", padx=2)
        
    def edit_action(self, idx):
        if idx >= len(self.actions):
            return
            
        action = self.actions[idx]
        
        edit_win = ctk.CTkToplevel(self.window)
        edit_win.title(f"Chỉnh sửa hành động {idx+1}")
        edit_win.geometry("400x300")
        edit_win.grab_set()
        
        ctk.CTkLabel(edit_win, text=f"Vị trí: {action['position']} (chỉ xem)").pack(pady=10)
        
        ctk.CTkLabel(edit_win, text="Thời gian thực hiện (ms):").pack(pady=5)
        duration_entry = ctk.CTkEntry(edit_win, width=200)
        duration_entry.insert(0, str(action['duration']))
        duration_entry.pack(pady=5)
        
        ctk.CTkLabel(edit_win, text="Delay sau hành động (ms):").pack(pady=5)
        delay_entry = ctk.CTkEntry(edit_win, width=200)
        delay_entry.insert(0, str(action['delay']))
        delay_entry.pack(pady=5)
        
        def save_changes():
            try:
                action['duration'] = int(duration_entry.get())
                action['delay'] = int(delay_entry.get())
                self.update_action_display()
                edit_win.destroy()
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ")
                
        ctk.CTkButton(edit_win, text="💾 Lưu", command=save_changes).pack(pady=20)
        
    def move_action(self, idx, direction):
        new_idx = idx + direction
        if 0 <= new_idx < len(self.actions):
            self.actions[idx], self.actions[new_idx] = self.actions[new_idx], self.actions[idx]
            self.restart_all_clickers()
            
    def delete_action(self, idx):
        if idx < len(self.actions):
            if self.actions[idx]["process"]:
                self.actions[idx]["process"].terminate()
            del self.actions[idx]
            self.restart_all_clickers()
            
    def restart_all_clickers(self):
        # Tắt tất cả clicker
        for action in self.actions:
            if action.get("process"):
                action["process"].terminate()
                
        # Khởi động lại
        script_dir = os.path.dirname(os.path.abspath(__file__))
        clicker_path = os.path.join(script_dir, "clicker.py")
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable
            
        for idx, action in enumerate(self.actions):
            cmd = [python_exe, clicker_path, 
                   f"--port={self.server_port}", 
                   f"--location={idx}", 
                   f"--type={action['type']}"]
            action["process"] = subprocess.Popen(cmd, 
                                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
                                                
        self.update_action_display()
        
    def start_clicking(self):
        if not self.actions:
            messagebox.showwarning("Cảnh báo", "Chưa có hành động nào!")
            return
            
        # Kiểm tra vị trí đã được set chưa
        for action in self.actions:
            if action["position"] == "0x0":
                messagebox.showwarning("Cảnh báo", "Vui lòng đặt vị trí cho tất cả các hành động!")
                return
                
        self.is_running = True
        self.stop_flag = False
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # Tắt tất cả clicker
        for action in self.actions:
            if action.get("process"):
                action["process"].terminate()
                
        # Chạy clicking trong thread riêng
        thread = threading.Thread(target=self.run_clicking, daemon=True)
        thread.start()
        
    def run_clicking(self):
        mode = self.repeat_mode.get()
        
        if mode == "infinite":
            while not self.stop_flag:
                self.execute_actions()
        elif mode == "times":
            try:
                times = int(self.repeat_value.get())
                for _ in range(times):
                    if self.stop_flag:
                        break
                    self.execute_actions()
            except ValueError:
                messagebox.showerror("Lỗi", "Số lần không hợp lệ")
        elif mode == "minutes":
            try:
                minutes = int(self.repeat_value.get())
                end_time = time.time() + minutes * 60
                while time.time() < end_time and not self.stop_flag:
                    self.execute_actions()
            except ValueError:
                messagebox.showerror("Lỗi", "Số phút không hợp lệ")
                
        self.window.after(0, self.on_clicking_finished)
        
    def execute_actions(self):
        for action in self.actions:
            if self.stop_flag:
                break
                
            x, y = map(int, action["position"].split("x"))
            duration = action["duration"] / 1000.0
            
            if action["type"] == "left":
                pyautogui.click(x, y, duration=duration)
            elif action["type"] == "right":
                pyautogui.rightClick(x, y, duration=duration)
            elif action["type"] == "double":
                pyautogui.doubleClick(x, y, interval=duration)
                
            time.sleep(action["delay"] / 1000.0)
            
    def stop_clicking(self):
        self.stop_flag = True
        
    def on_clicking_finished(self):
        self.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.restart_all_clickers()
        
    def save_config(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json")])
        if filename:
            config = {
                "actions": [{
                    "type": a["type"],
                    "position": a["position"],
                    "duration": a["duration"],
                    "delay": a["delay"]
                } for a in self.actions],
                "repeat_mode": self.repeat_mode.get(),
                "repeat_value": self.repeat_value.get()
            }
            with open(filename, "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Thành công", "Đã lưu cấu hình!")
            
    def load_config(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, "r") as f:
                config = json.load(f)
                
            # Xóa các action hiện tại
            for action in self.actions:
                if action.get("process"):
                    action["process"].terminate()
            self.actions.clear()
            
            # Load config
            self.repeat_mode.set(config.get("repeat_mode", "infinite"))
            self.repeat_value.delete(0, "end")
            self.repeat_value.insert(0, config.get("repeat_value", ""))
            
            # Tạo lại các action
            for action_data in config["actions"]:
                self.actions.append({
                    "type": action_data["type"],
                    "position": action_data["position"],
                    "duration": action_data["duration"],
                    "delay": action_data["delay"],
                    "process": None
                })
                
            self.restart_all_clickers()
            messagebox.showinfo("Thành công", "Đã load cấu hình!")
            
    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
        
    def on_closing(self):
        for action in self.actions:
            if action.get("process"):
                action["process"].terminate()
        if self.server_socket:
            self.server_socket.close()
        self.window.destroy()

if __name__ == "__main__":
    app = EasyClicker()
    app.run()
