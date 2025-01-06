import requests
import random
import time
from bs4 import BeautifulSoup
import os

# Mảng các route mà client sẽ truy cập
routes = [
    '/',
    '/about',
    '/contact'
]

# URL của server Flask (vì sử dụng SSL/TLS nên là https)
server_url = "https://localhost:5000"

# Các tài nguyên mà client sẽ tải xuống (CSS, JS)
def download_resource(resource_url):
    try:
        # Gửi yêu cầu GET đến tài nguyên (CSS, JS)
        response = requests.get(resource_url, verify=False)
        
        if response.status_code == 200:
            print(f"Successfully downloaded {resource_url}")
        else:
            print(f"Failed to download {resource_url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while downloading {resource_url}: {e}")

# Phân tích và tải tài nguyên (CSS, JS) từ nội dung HTML
def download_assets(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Tìm tất cả các link CSS
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href:
            resource_url = href if href.startswith('http') else base_url + href
            download_resource(resource_url)
    
    # Tìm tất cả các script JS
    for script in soup.find_all('script', src=True):
        src = script.get('src')
        if src:
            resource_url = src if src.startswith('http') else base_url + src
            download_resource(resource_url)

def access_random_page():
    # Chọn ngẫu nhiên một route
    route = random.choice(routes)
    url = server_url + route
    
    try:
        # Gửi yêu cầu GET đến trang HTML
        response = requests.get(url, verify=False)
        
        # Kiểm tra xem trang có được tải thành công không (HTTP 200)
        if response.status_code == 200:
            print(f"Successfully accessed {url}")
            print(response.text)  # In ra nội dung của trang
            
            # Sau khi tải trang HTML thành công, tải các tài nguyên liên quan (CSS, JS)
            download_assets(response.text, server_url)
        else:
            print(f"Failed to access {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while accessing {url}: {e}")
        # Sleep một khoảng thời gian ngẫu nhiên từ 1 đến 5 giây
        sleep_time = random.randint(1, 5)
        print(f"Sleeping for {sleep_time} seconds before the next request...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    # Client sẽ truy cập các route ngẫu nhiên 1000 lần
    for _ in range(1000):
        access_random_page()
