Nếu có vấn đề nào liên quan bạn có thể gửi mail cho mình hoặc comment trực tiếp trong video!

# Hướng dẫn Cài đặt trên Windows (WSL)

## Bước 1 – Cài đặt WSL (Ubuntu)

1. Mở **PowerShell** với quyền **Administrator**.  
2. Chạy lệnh:  
   ```powershell
   wsl --install
   ```
Khi được hỏi, hãy cấp quyền quản trị và chờ Ubuntu cài đặt.

Sau khi xong, khởi chạy WSL:
```powershell
wsl
```

Thiết lập tên người dùng và mật khẩu cho Ubuntu (tách biệt với Windows).

Kiểm tra cơ bản trong Ubuntu:

```powershell
pwd   # Hiển thị thư mục hiện tại
ls    # Liệt kê file/thư mục
cd ~  # Trở về home directory
```

💡 Lưu ý: Hệ thống file trong WSL khác với Windows. Để tránh lỗi phân quyền và giảm lag, hãy đặt toàn bộ project bên trong WSL (thư mục home Linux).

### Bước 2 – Cài đặt Conda trong WSL

Ta sẽ dùng Miniconda để gọn nhẹ hơn.

Trong terminal Ubuntu, chạy:
```powershell
# Tải Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```
```powershell
# Cài đặt
bash Miniconda3-latest-Linux-x86_64.sh
```

Chấp nhận license.

Giữ nguyên đường dẫn mặc định: /home/<tên-username>/miniconda3.

Chọn Yes để Conda tự khởi tạo.

Đóng và mở lại Ubuntu, sau đó kiểm tra:
```powershell
conda --version
```

### Bước 3 – Clone Repository trong WSL
```powershell
cd ~
mkdir projects
cd projects
git clone https://github.com/timi1511/agents.git
cd agents
```

### Bước 4 – Tạo môi trường Conda

Trong thư mục agents:

```powershell
conda create -n mcp python=3.12 -y
conda activate mcp
```

Cài dependencies:
```powershell
pip install -r requirements.txt
```

(hoặc cài thủ công các gói được liệt kê trong requirements.txt).

### Bước 5 – Thiết lập VS Code cho WSL

Mở VS Code trên Windows.

Cài extension: Remote - WSL (by Microsoft).

Nhấn:

Ctrl + Shift + P → Remote-WSL: New Window


Điều hướng đến project:

/home/<tên-username>/projects/agents


Cài thêm extension trong WSL:

Python (ms-python)

Jupyter (microsoft)

### Bước 6 – Khởi động lại & chạy dự án

Mở lại PowerShell trên Windows.

Vào WSL:
```powershell
wsl
```

Điều hướng đến project và bật môi trường:
```powershell
cd ~/projects/agents
conda activate mcp
code .
```
