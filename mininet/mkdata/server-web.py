
from flask import Flask, render_template
import os

app = Flask(__name__, template_folder='templates')

# Định nghĩa các route và liên kết với các trang HTML
routes = [
    '/',
    '/about',
    '/contact'
]

# Duyệt qua mảng các route và tạo các hàm view
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Cấu hình ứng dụng Flask để tìm các file tĩnh trong thư mục static
app.config['STATIC_FOLDER'] = 'static'

if __name__ == "__main__":
    # Chạy server với chứng chỉ SSL
    app.run(host='0.0.0.0', port=5000, ssl_context=('server.crt', 'server.key'))
