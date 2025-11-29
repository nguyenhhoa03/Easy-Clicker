import tkinter as tk
import socket
import json
import argparse
import time
import threading

class ClickerWindow:
    def __init__(self, port, location, click_type, number):
        self.port = port
        self.location = location
        self.click_type = click_type
        self.number = number
        self.last_position = None
        self.position_stable_time = None
        self.should_exit = False
        
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        # Kích thước cửa sổ
        self.window_size = 50
        
        # Đặt vị trí cửa sổ
        x = location[0] - self.window_size // 2
        y = location[1] - self.window_size // 2
        self.root.geometry(f"{self.window_size}x{self.window_size}+{x}+{y}")
        
        # Tạo canvas trong suốt
        self.canvas = tk.Canvas(self.root, width=self.window_size, height=self.window_size, 
                                bg='black', highlightthickness=0)
        self.canvas.pack()
        
        # Làm cửa sổ trong suốt
        self.root.wm_attributes("-transparentcolor", "black")
        
        # Vẽ vòng tròn và text
        self.draw_circle()
        
        # Bind sự kiện kéo thả
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.drag_data = {"x": 0, "y": 0}
        
        # Thread kiểm tra vị trí
        self.check_thread = threading.Thread(target=self.check_position, daemon=True)
        self.check_thread.start()
        
        # Thread lắng nghe lệnh từ server
        self.listen_thread = threading.Thread(target=self.listen_commands, daemon=True)
        self.listen_thread.start()
        
    def listen_commands(self):
        """Lắng nghe lệnh từ server (như lệnh thoát)"""
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind(("127.0.0.1", 0))
        listen_port = listen_socket.getsockname()[1]
        listen_socket.listen(1)
        
        # Gửi port lắng nghe về server (nếu cần mở rộng sau)
        # Hiện tại clicker sẽ tự thoát khi nhận được lệnh
        
        while not self.should_exit:
            try:
                listen_socket.settimeout(1.0)
                # Đơn giản hóa: clicker sẽ tự đóng khi main app đóng connection
            except:
                pass
        
    def draw_circle(self):
        # Xóa canvas
        self.canvas.delete("all")
        
        # Vẽ vòng tròn ngoài (màu xanh)
        self.canvas.create_oval(2, 2, self.window_size-2, self.window_size-2, 
                                fill="#1f538d", outline="#3b8ed0", width=2)
        
        # Hiển thị số
        display_text = str(self.number)
            
        self.canvas.create_text(self.window_size//2, self.window_size//2, 
                                text=display_text, fill="white", 
                                font=("Arial", 12, "bold"))
        
    def on_press(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_data["x"]
        y = self.root.winfo_y() + event.y - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")
        
    def on_release(self, event):
        pass
        
    def check_position(self):
        while not self.should_exit:
            time.sleep(0.1)
            
            current_x = self.root.winfo_x() + self.window_size // 2
            current_y = self.root.winfo_y() + self.window_size // 2
            current_position = (current_x, current_y)
            
            if self.last_position is None:
                self.last_position = current_position
                self.position_stable_time = time.time()
                continue
                
            # Kiểm tra vị trí có thay đổi không
            if current_position != self.last_position:
                self.last_position = current_position
                self.position_stable_time = time.time()
            else:
                # Vị trí ổn định
                if time.time() - self.position_stable_time >= 0.3:
                    # Gửi vị trí về server
                    self.send_position(current_position)
                    self.position_stable_time = time.time() + 3600  # Tránh gửi liên tục
                    
    def send_position(self, position):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", self.port))
            
            message = {
                "type": "position_update",
                "number": self.number,
                "position": position
            }
            
            client.send(json.dumps(message).encode())
            client.close()
        except Exception as e:
            print(f"Error sending position: {e}")
            
    def run(self):
        # Kiểm tra định kỳ nếu cần thoát
        def check_exit():
            if self.should_exit:
                self.root.destroy()
            else:
                self.root.after(100, check_exit)
        
        self.root.after(100, check_exit)
        self.root.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--location", type=str, required=True)
    parser.add_argument("--type", type=str, required=True)
    parser.add_argument("--number", type=int, required=True)
    
    args = parser.parse_args()
    
    # Parse location
    location = tuple(map(int, args.location.split(",")))
    
    app = ClickerWindow(args.port, location, args.type, args.number)
    app.run()
