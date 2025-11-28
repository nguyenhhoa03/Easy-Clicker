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
        
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        # Kích thước cửa sổ
        self.window_size = 45
        
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
        
    def draw_circle(self):
        # Xóa canvas
        self.canvas.delete("all")
        
        # Vẽ vòng tròn ngoài (màu xanh)
        self.canvas.create_oval(2, 2, self.window_size-2, self.window_size-2, 
                                fill="#1f538d", outline="#3b8ed0", width=2)
        
        # Hiển thị số và chữ
        display_text = str(self.number)
        if self.click_type == "s":
            display_text += "S"
        elif self.click_type == "e":
            display_text += "E"
            
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
        while True:
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
                    self.position_stable_time = time.time() + 10  # Tránh gửi liên tục
                    
    def send_position(self, position):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", self.port))
            
            message = {
                "type": "position_update",
                "number": self.number,
                "position": position
            }
            
            if self.click_type in ["s", "e"]:
                message["drag_type"] = self.click_type
                
            client.send(json.dumps(message).encode())
            client.close()
        except Exception as e:
            print(f"Error sending position: {e}")
            
    def run(self):
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
