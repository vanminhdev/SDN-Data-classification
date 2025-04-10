
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='static', static_url_path='')

if __name__ == "__main__":
    # Chạy server với chứng chỉ SSL
    app.run(host='0.0.0.0', port=5000, ssl_context=('server.crt', 'server.key'))
