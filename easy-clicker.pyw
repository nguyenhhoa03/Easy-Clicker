import customtkinter as ctk
import subprocess
import socket
import threading
import json
import pyautogui
import time
from tkinter import filedialog, messagebox
import os

class ClickAction:
    def __init__(self, action_type, position, button="left", duration=300, delay=300, number=1):
        self.action_type = action_type  # "click"
        self.position = position  # (x, y)
        self.button = button  # "left", "right", "double"
        self.duration = duration
        self.delay = delay
        self.number = number

class EasyClicker:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Easy Clicker")
        self.app.geometry("800x600")
        
        self.actions = []
        self.clicker_processes = {}
        self.server_socket = None
        self.server_port = 0
        self.is_running = False
        self.stop_flag = False
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
        self.start_server()
        
    def setup_ui(self):
        # Top controls
        top_frame = ctk.CTkFrame(self.app)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(top_frame, text="Thêm Click", command=self.add_click).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Load Config", command=self.load_config).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Lưu Config", command=self.save_config).pack(side="left", padx=5)
        
        # Loop settings
        loop_frame = ctk.CTkFrame(self.app)
        loop_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(loop_frame, text="Lặp lại:").pack(side="left", padx=5)
        
        self.loop_type = ctk.StringVar(value="infinite")
        ctk.CTkRadioButton(loop_frame, text="Vô hạn", variable=self.loop_type, value="infinite").pack(side="left", padx=5)
        ctk.CTkRadioButton(loop_frame, text="N lần", variable=self.loop_type, value="times").pack(side="left", padx=5)
        ctk.CTkRadioButton(loop_frame, text="N phút", variable=self.loop_type, value="minutes").pack(side="left", padx=5)
        
        self.loop_value = ctk.CTkEntry(loop_frame, width=80, placeholder_text="Số lần/phút")
        self.loop_value.pack(side="left", padx=5)
        
        # Actions list with scrollbar
        actions_frame = ctk.CTkFrame(self.app)
        actions_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(actions_frame, text="Danh sách hành động:", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=5)
        
        self.actions_canvas_frame = ctk.CTkScrollableFrame(actions_frame, width=760, height=300)
        self.actions_canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Control buttons
        control_frame = ctk.CTkFrame(self.app)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_btn = ctk.CTkButton(control_frame, text="Bắt đầu", command=self.start_clicking, fg_color="green")
        self.start_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        self.stop_btn = ctk.CTkButton(control_frame, text="Dừng", command=self.stop_clicking, fg_color="red", state="disabled")
        self.stop_btn.pack(side="left", padx=5, expand=True, fill="x")
        
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("127.0.0.1", 0))
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
            message = json.loads(data)
            
            if message["type"] == "position_update":
                number = message["number"]
                position = message["position"]
                
                for action in self.actions:
                    if action.number == number:
                        action.position = tuple(position)
                        break
                
                self.app.after(0, self.refresh_actions_list)
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client.close()
            
    def add_click(self):
        button_dialog = ctk.CTkToplevel(self.app)
        button_dialog.title("Chọn loại click")
        button_dialog.geometry("300x250")
        button_dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(button_dialog, text="Chọn loại click:").pack(pady=20)
        
        def choose_left():
            button_dialog.destroy()
            self.create_clicker("left")
            
        def choose_right():
            button_dialog.destroy()
            self.create_clicker("right")
            
        def choose_double():
            button_dialog.destroy()
            self.create_clicker("double")
            
        ctk.CTkButton(button_dialog, text="Chuột Trái", command=choose_left).pack(pady=5)
        ctk.CTkButton(button_dialog, text="Chuột Phải", command=choose_right).pack(pady=5)
        ctk.CTkButton(button_dialog, text="Double Click", command=choose_double).pack(pady=5)
        
    def create_clicker(self, button_type):
        number = len(self.actions) + 1
        action = ClickAction("click", (100, 100), button_type, number=number)
        self.actions.append(action)
        
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        location = (screen_width // 2, screen_height // 2)
        
        # Lấy đường dẫn tuyệt đối của clicker.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        clicker_path = os.path.join(current_dir, "clicker.py")
            
        cmd = [
            "python", clicker_path,
            f"--port={self.server_port}",
            f"--location={location[0]},{location[1]}",
            f"--type={button_type}",
            f"--number={number}"
        ]
        
        process = subprocess.Popen(cmd)
        self.clicker_processes[str(number)] = process
        
        self.refresh_actions_list()
        
    def refresh_actions_list(self):
        for widget in self.actions_canvas_frame.winfo_children():
            widget.destroy()
            
        for i, action in enumerate(self.actions):
            self.create_action_widget(action, i)
            
    def create_action_widget(self, action, index):
        frame = ctk.CTkFrame(self.actions_canvas_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        pos_str = f"{action.position[0]}x{action.position[1]}" if action.position else "Chưa đặt"
        
        if action.button == "left":
            text = f"{action.number}: Click chuột trái tại vị trí {pos_str} trong {action.duration}ms"
        elif action.button == "right":
            text = f"{action.number}: Click chuột phải tại vị trí {pos_str} trong {action.duration}ms"
        else:  # double
            text = f"{action.number}: Double click tại vị trí {pos_str}"
            
        label = ctk.CTkLabel(frame, text=text, anchor="w")
        label.pack(side="left", fill="x", expand=True, padx=5)
        
        delay_label = ctk.CTkLabel(frame, text=f"Delay {action.delay}ms")
        delay_label.pack(side="left", padx=5)
        
        # Buttons
        ctk.CTkButton(frame, text="⚙️", width=30, command=lambda a=action: self.edit_action(a)).pack(side="left", padx=2)
        ctk.CTkButton(frame, text="↑", width=30, command=lambda idx=index: self.move_up(idx)).pack(side="left", padx=2)
        ctk.CTkButton(frame, text="↓", width=30, command=lambda idx=index: self.move_down(idx)).pack(side="left", padx=2)
        ctk.CTkButton(frame, text="🗑️", width=30, command=lambda idx=index: self.delete_action(idx)).pack(side="left", padx=2)
        
    def edit_action(self, action):
        edit_window = ctk.CTkToplevel(self.app)
        edit_window.title(f"Chỉnh sửa hành động {action.number}")
        edit_window.geometry("400x300")
        edit_window.attributes("-topmost", True)
        
        ctk.CTkLabel(edit_window, text="Thời gian thực hiện (ms):").pack(pady=5)
        duration_entry = ctk.CTkEntry(edit_window)
        duration_entry.insert(0, str(action.duration))
        duration_entry.pack(pady=5)
        
        ctk.CTkLabel(edit_window, text="Delay sau hành động (ms):").pack(pady=5)
        delay_entry = ctk.CTkEntry(edit_window)
        delay_entry.insert(0, str(action.delay))
        delay_entry.pack(pady=5)
        
        # Hiển thị loại click
        if action.button == "left":
            click_type = "Click chuột trái"
        elif action.button == "right":
            click_type = "Click chuột phải"
        else:
            click_type = "Double click"
            
        ctk.CTkLabel(edit_window, text=f"Loại: {click_type}").pack(pady=5)
        ctk.CTkLabel(edit_window, text=f"Tọa độ: {action.position} (chỉ xem)").pack(pady=5)
            
        def save_changes():
            try:
                action.duration = int(duration_entry.get())
                action.delay = int(delay_entry.get())
                self.refresh_actions_list()
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ")
                
        ctk.CTkButton(edit_window, text="Lưu", command=save_changes).pack(pady=20)
        
    def move_up(self, index):
        if index > 0:
            self.actions[index], self.actions[index-1] = self.actions[index-1], self.actions[index]
            self.renumber_actions()
            self.update_clicker_numbers()
            
    def move_down(self, index):
        if index < len(self.actions) - 1:
            self.actions[index], self.actions[index+1] = self.actions[index+1], self.actions[index]
            self.renumber_actions()
            self.update_clicker_numbers()
            
    def renumber_actions(self):
        for i, action in enumerate(self.actions):
            action.number = i + 1
        self.refresh_actions_list()
        
    def update_clicker_numbers(self):
        # Gửi lệnh cập nhật số thứ tự cho tất cả clicker
        for key, process in list(self.clicker_processes.items()):
            try:
                process.terminate()
            except:
                pass
                
        self.clicker_processes.clear()
        
        # Tạo lại các clicker với số mới
        for action in self.actions:
            self.recreate_clicker(action)
                
    def recreate_clicker(self, action):
        position = action.position if action.position else (100, 100)
        
        # Lấy đường dẫn tuyệt đối của clicker.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        clicker_path = os.path.join(current_dir, "clicker.py")
            
        cmd = [
            "python", clicker_path,
            f"--port={self.server_port}",
            f"--location={position[0]},{position[1]}",
            f"--type={action.button}",
            f"--number={action.number}"
        ]
        
        process = subprocess.Popen(cmd)
        self.clicker_processes[str(action.number)] = process
        
    def delete_action(self, index):
        action = self.actions[index]
        
        # Đóng các clicker liên quan
        key = str(action.number)
        if key in self.clicker_processes:
            self.clicker_processes[key].terminate()
            del self.clicker_processes[key]
                
        del self.actions[index]
        self.renumber_actions()
        self.update_clicker_numbers()
        
    def close_all_clickers(self):
        for process in self.clicker_processes.values():
            try:
                process.terminate()
            except:
                pass
        self.clicker_processes.clear()
        
    def start_clicking(self):
        if not self.actions:
            messagebox.showwarning("Cảnh báo", "Chưa có hành động nào!")
            return
            
        # Kiểm tra tọa độ đã đặt chưa
        for action in self.actions:
            if not action.position:
                messagebox.showwarning("Cảnh báo", f"Hành động {action.number} chưa đặt tọa độ!")
                return
                
        self.is_running = True
        self.stop_flag = False
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # Đóng tất cả clicker
        self.close_all_clickers()
        
        # Bắt đầu thực hiện
        thread = threading.Thread(target=self.execute_actions, daemon=True)
        thread.start()
        
    def execute_actions(self):
        loop_type = self.loop_type.get()
        loop_count = 0
        start_time = time.time()
        
        try:
            if loop_type == "infinite":
                while not self.stop_flag:
                    self.perform_actions()
            elif loop_type == "times":
                try:
                    times = int(self.loop_value.get())
                    for _ in range(times):
                        if self.stop_flag:
                            break
                        self.perform_actions()
                except ValueError:
                    self.app.after(0, lambda: messagebox.showerror("Lỗi", "Số lần không hợp lệ"))
                    return
            elif loop_type == "minutes":
                try:
                    minutes = float(self.loop_value.get())
                    end_time = start_time + (minutes * 60)
                    while time.time() < end_time and not self.stop_flag:
                        self.perform_actions()
                except ValueError:
                    self.app.after(0, lambda: messagebox.showerror("Lỗi", "Số phút không hợp lệ"))
                    return
        finally:
            self.is_running = False
            self.app.after(0, self.finish_clicking)
            
    def perform_actions(self):
        for action in self.actions:
            if self.stop_flag:
                break
                
            if action.button == "double":
                # Double click
                pyautogui.doubleClick(action.position[0], action.position[1])
            else:
                # Click thường (trái/phải)
                pyautogui.click(action.position[0], action.position[1], 
                               button=action.button, 
                               duration=action.duration/1000.0)
                                
            time.sleep(action.delay/1000.0)
            
    def stop_clicking(self):
        self.stop_flag = True
        
    def finish_clicking(self):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        # Hiển thị lại các clicker
        for action in self.actions:
            self.recreate_clicker(action)
                
    def save_config(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", 
                                                filetypes=[("JSON files", "*.json")])
        if filename:
            config = {
                "actions": [],
                "loop_type": self.loop_type.get(),
                "loop_value": self.loop_value.get()
            }
            
            for action in self.actions:
                action_data = {
                    "type": action.action_type,
                    "position": action.position,
                    "button": action.button,
                    "duration": action.duration,
                    "delay": action.delay,
                    "number": action.number
                }
                config["actions"].append(action_data)
                
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                
            messagebox.showinfo("Thành công", "Đã lưu cấu hình!")
            
    def load_config(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            # Đóng tất cả clicker hiện tại
            self.close_all_clickers()
            self.actions.clear()
            
            # Load cấu hình
            self.loop_type.set(config.get("loop_type", "infinite"))
            self.loop_value.delete(0, "end")
            self.loop_value.insert(0, config.get("loop_value", ""))
            
            for action_data in config["actions"]:
                action = ClickAction(
                    action_data["type"],
                    action_data["position"],
                    action_data["button"],
                    action_data["duration"],
                    action_data["delay"],
                    action_data["number"]
                )
                self.actions.append(action)
                self.recreate_clicker(action)
                    
            self.refresh_actions_list()
            messagebox.showinfo("Thành công", "Đã load cấu hình!")
            
    def run(self):
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()
        
    def on_closing(self):
        self.close_all_clickers()
        try:
            self.server_socket.close()
        except:
            pass
        self.app.destroy()

if __name__ == "__main__":
    app = EasyClicker()
    app.run()
