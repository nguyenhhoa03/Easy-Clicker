import tkinter as tk
import socket
import sys
import time
import threading

class ClickerWindow:
    def __init__(self, port, location, click_type, position=None):
        self.port = port
        self.location = location
        self.click_type = click_type
        self.last_position = None
        self.position_stable_time = 0
        self.initial_position = position  # Vị trí ban đầu nếu có
        
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Màu nền trong suốt
        bg_color = "#FF00FF"
        self.root.configure(bg=bg_color)
        self.root.wm_attributes("-transparentcolor", bg_color)
        
        # Kích thước cửa sổ
        size = 40
        
        # Đặt vị trí ban đầu
        if position and position != "0x0":
            x, y = map(int, position.split("x"))
            # Trừ đi size/2 để căn giữa
            self.root.geometry(f"{size}x{size}+{x-20}+{y-20}")
        else:
            self.root.geometry(f"{size}x{size}+100+100")
        
        # Tạo canvas để vẽ vòng tròn
        self.canvas = tk.Canvas(self.root, width=size, height=size, 
                               bg=bg_color, highlightthickness=0)
        self.canvas.pack()
        
        # Màu sắc theo loại click
        color_map = {
            "left": "#4CAF50",
            "right": "#2196F3",
            "double": "#FF9800"
        }
        color = color_map.get(click_type, "#4CAF50")
        
        # Vẽ vòng tròn
        self.canvas.create_oval(2, 2, size-2, size-2, fill=color, outline="white", width=2)
        
        # Hiển thị số thứ tự
        self.text_id = self.canvas.create_text(size//2, size//2, 
                                               text=str(int(location)+1), 
                                               fill="white", 
                                               font=("Arial", 14, "bold"))
        
        # Bind sự kiện kéo thả
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        
        self.drag_data = {"x": 0, "y": 0}
        
        # Bắt đầu kiểm tra vị trí
        self.check_position()
        
    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_data["x"]
        y = self.root.winfo_y() + event.y - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")
        
    def stop_drag(self, event):
        pass
        
    def check_position(self):
        # Lấy vị trí trung tâm của cửa sổ
        x = self.root.winfo_x() + 20  # 20 = size/2
        y = self.root.winfo_y() + 20
        current_pos = (x, y)
        
        # Kiểm tra nếu vị trí không đổi trong 300ms
        if self.last_position == current_pos:
            if time.time() - self.position_stable_time >= 0.3:
                # Gửi vị trí về server
                self.send_position(x, y)
                self.position_stable_time = time.time() + 100  # Đặt thời gian lớn để không gửi lại
        else:
            self.last_position = current_pos
            self.position_stable_time = time.time()
            
        # Tiếp tục kiểm tra
        self.root.after(50, self.check_position)
        
    def send_position(self, x, y):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('127.0.0.1', self.port))
            message = f"POS:{self.location}:{x}x{y}"
            client.send(message.encode())
            client.close()
        except Exception as e:
            print(f"Error sending position: {e}")
            
    def run(self):
        self.root.mainloop()

def parse_args():
    args = {}
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            key, value = arg[2:].split("=", 1)
            args[key] = value
    return args

if __name__ == "__main__":
    args = parse_args()
    
    port = int(args.get("port", 0))
    location = args.get("location", "0")
    click_type = args.get("type", "left")
    position = args.get("position", None)  # Lấy vị trí nếu có
    
    app = ClickerWindow(port, location, click_type, position)
    app.run()
