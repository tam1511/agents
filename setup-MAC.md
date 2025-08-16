# Setup environment for MAC

Nếu có vấn đề nào liên quan các bạn có thể gửi mail cho mình hoặc comment trực tiếp trong video. Mình sẽ trả lời sớm nhất có thể!

# Hướng dẫn Cài đặt

## Phần 1: Clone Repository

Lấy bản sao của mã nguồn về máy tính của bạn.

1. **Cài đặt Git** (nếu chưa có)  
   - Trên hầu hết máy Mac, Git thường đã được cài đặt sẵn.  
   - Kiểm tra bằng lệnh:  
     ```bash
     git --version
     ```  
   - Nếu chưa có, hệ thống sẽ yêu cầu bạn cài đặt.

2. **Mở Terminal**  
   - Vào: `Applications > Utilities > Terminal`.

3. **Điều hướng đến thư mục dự án**  
   - Nếu bạn đã có thư mục `projects`, di chuyển vào nó:  
     ```bash
     cd ~/projects
     ```  
   - Nếu chưa có, hãy tạo mới:  
     ```bash
     mkdir ~/projects
     cd ~/projects
     ```

4. **Clone repo**  
   - Chạy lệnh sau trong thư mục `projects`:  
     ```bash
     git clone https://github.com/tam1511/agents
     ```  
   - Thư mục mới có tên **agents** sẽ được tạo ra và chứa toàn bộ mã nguồn.  
   - Chuyển vào thư mục con `curator`:  
     ```bash
     cd agents/curator
     ```  
   - Lúc này, thư mục `agents` được gọi là **project root directory** (thư mục gốc của dự án).

---

## Phần 2: Cài đặt môi trường Anaconda (nếu chưa có)

### 1. Tải và cài đặt Anaconda
- Tải tại: [Anaconda Download](https://docs.anaconda.com/anaconda/install/mac-os/)  
- Chạy file cài đặt và làm theo hướng dẫn.  
- Lưu ý: Anaconda chiếm vài GB dung lượng và cài đặt có thể mất nhiều thời gian.

### 2. Thiết lập môi trường
1. Mở **Terminal mới**.  
2. Điều hướng đến thư mục gốc của dự án:  
   ```bash
   cd ~/Documents/Projects/agents
   ls
(dùng ls để kiểm tra các thư mục con trong dự án).

3. Tạo môi trường mới:

```bash
conda create -n mcp python=3.12 -y
```

Quá trình này có thể mất 20–30 phút nếu đây là lần đầu cài đặt Anaconda.

Nếu gặp lỗi, có thể cân nhắc dùng Miniconda hoặc Virtual Environment thay thế.

Kích hoạt môi trường:

```bash
conda activate mcp
```
---

## Phần 3: Cài đặt Dependencies

### 1. Kiểm tra file yêu cầu
Trong thư mục gốc của dự án (`agents/`), bạn sẽ thấy file **requirements.txt** .  
File này chứa danh sách tất cả thư viện Python cần thiết.

### 2. Cài đặt dependencies với pip
Đảm bảo bạn đã kích hoạt môi trường conda `mcp`:  

```bash
conda activate mcp
```

Sau đó, chạy:
```bash
pip install -r requirements.txt
```

Bắt đầu với VS Code

Mở dự án trong Visual Studio Code bằng lệnh:

```bash
code .
```
