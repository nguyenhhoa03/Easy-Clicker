# Easy Clicker

## ⚠️ Cảnh báo: Ứng dụng chưa được tối ưu và tốn rất nhiều tài nguyên thiết bị khi có nhiều thao tác.

Ứng dụng tự động hóa thao tác chuột với giao diện đồ họa thân thiện, cho phép ghi lại và thực thi các chuỗi thao tác click chuột trên Windows.

## Tính năng

- **Đa dạng loại click**: Click trái, click phải, double click
- **Tùy chỉnh chi tiết**: Điều chỉnh vị trí, thời gian thực hiện và delay cho từng hành động
- **Quản lý hành động**: Thêm, xóa, sửa, sắp xếp thứ tự các hành động
- **Chế độ lặp linh hoạt**: 
  - Lặp vô hạn
  - Lặp N lần
  - Lặp trong N phút
- **Lưu/Load cấu hình**: Lưu và tải lại các chuỗi hành động qua file JSON
- **Giao diện hiện đại**: Sử dụng CustomTkinter với theme tối

## Yêu cầu hệ thống

- **Hệ điều hành**: Windows 10/11
- **Python**: 3.7 trở lên

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/nguyenhhoa03/Easy-Clicker.git
cd Easy-Clicker
```

### 2. Cài đặt các thư viện phụ thuộc

```bash
pip install -r requirements.txt
```

## Cấu trúc dự án

```
Easy-Clicker/
├── easy-clicker.pyw             # File chính chứa giao diện và logic
├── clicker.py           # Module xử lý click (subprocess)
├── requirements.txt     # Danh sách thư viện phụ thuộc
├── LICENSE             # GNU General Public License v3.0
└── README.md           # Tài liệu hướng dẫn
```

## Hướng dẫn sử dụng

### 1. Khởi chạy ứng dụng

```bash
python easy-clicker.pyw
```

### 2. Thêm hành động

- Click vào **➕ Click Trái/Phải/Nháy Đúp** để thêm hành động mới
- Một cửa sổ nhỏ sẽ xuất hiện cho phép bạn chọn vị trí click trên màn hình
- Nhấn **Enter** hoặc click chuột để xác nhận vị trí

### 3. Chỉnh sửa hành động

- Click nút **⚙️** bên cạnh hành động để chỉnh sửa:
  - **Thời gian thực hiện**: Thời gian di chuyển chuột đến vị trí (ms)
  - **Delay**: Thời gian chờ sau khi thực hiện hành động (ms)

### 4. Sắp xếp hành động

- **🔼**: Di chuyển hành động lên trên
- **🔽**: Di chuyển hành động xuống dưới
- **❌**: Xóa hành động

### 5. Cấu hình chế độ lặp

- **Vô hạn**: Lặp liên tục cho đến khi dừng
- **N lần**: Nhập số lần lặp vào ô bên cạnh
- **N phút**: Nhập số phút chạy vào ô bên cạnh

### 6. Thực thi

- **▶️ Bắt Đầu**: Bắt đầu thực hiện chuỗi hành động
- **⏹️ Dừng**: Dừng thực hiện

### 7. Lưu/Load cấu hình

- **💾 Save**: Lưu cấu hình hiện tại ra file JSON
- **📁 Load**: Tải cấu hình từ file JSON đã lưu

## Ví dụ cấu hình JSON

```json
{
  "actions": [
    {
      "type": "left",
      "position": "500x300",
      "duration": 300,
      "delay": 300
    },
    {
      "type": "right",
      "position": "600x400",
      "duration": 300,
      "delay": 300
    }
  ],
  "repeat_mode": "times",
  "repeat_value": "10"
}
```

## Lưu ý kỹ thuật

### Kiến trúc

- **easy-clicker.pyw**: Giao diện chính sử dụng CustomTkinter, quản lý các subprocess clicker
- **clicker.py**: Module độc lập chạy trong subprocess để xử lý việc hiển thị vị trí click
- **Socket communication**: Server-client architecture để giao tiếp giữa main và clicker processes (localhost:dynamic_port)

### Thread-safe

- Sử dụng `daemon=True` cho background threads
- `window.after()` để cập nhật UI từ worker threads
- Flag `stop_flag` để dừng execution loop an toàn

### Windows-specific

- Sử dụng `pythonw.exe` để ẩn console window
- `CREATE_NO_WINDOW` flag cho subprocess
- Socket server chạy trên localhost (127.0.0.1)

## Xử lý sự cố

### Lỗi import module

```bash
pip install --upgrade -r requirements.txt
```

### Clicker không hoạt động

- Kiểm tra file `clicker.py` có tồn tại cùng thư mục với `main.py`
- Đảm bảo đã set vị trí cho tất cả các hành động trước khi chạy (không để vị trí mặc định "0x0")

### Lỗi port đã được sử dụng

- Ứng dụng tự động chọn port ngẫu nhiên, nếu vẫn gặp lỗi hãy khởi động lại ứng dụng

## Phát triển thêm

Các tính năng có thể mở rộng:

- Thêm hotkey để start/stop
- Ghi lại toàn bộ chuỗi thao tác từ chuột thực
- Thêm điều kiện logic (if/else, loops)
- Hỗ trợ thao tác bàn phím
- Chế độ random delay/position để mô phỏng hành vi người dùng tự nhiên hơn
- Export/import macro sang các format khác


Báo lỗi và đề xuất tính năng mới xin gửi qua [Issues](https://github.com/nguyenhhoa03/Easy-Clicker/issues).

## License

Dự án này được phân phối dưới GNU General Public License v3.0. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

```
Easy Clicker - Auto Mouse Clicker Tool
Copyright (C) 2024

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

## Tác giả

- GitHub: [@nguyenhhoa03](https://github.com/nguyenhhoa03)
- Repository: [Easy-Clicker](https://github.com/nguyenhhoa03/Easy-Clicker)

## Lưu ý pháp lý

⚠️ **Vui lòng sử dụng ứng dụng có trách nhiệm và tuân thủ các điều khoản sử dụng của các ứng dụng, game, website,... mà bạn tương tác.** 

Việc sử dụng công cụ tự động hóa có thể vi phạm Terms of Service của một số dịch vụ. Tác giả không chịu trách nhiệm cho bất kỳ hậu quả nào phát sinh từ việc sử dụng không đúng mục đích.

---

**Made with ❤️ for automation enthusiasts**