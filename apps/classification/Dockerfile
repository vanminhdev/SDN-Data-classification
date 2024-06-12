# Sử dụng hình ảnh Python chính thức
FROM python:3.11-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt vào thư mục làm việc
COPY requirements.txt .

# Cài đặt các phụ thuộc
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào thư mục làm việc
COPY . .

# Mở cổng 5000
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["python", "app.py"]
