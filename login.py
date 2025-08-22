from selenium import webdriver
from selenium.webdriver import Chrome, Firefox, Edge, Safari
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.edge.options import Options as EdgeOptions

import time
import os
import requests
import json
import subprocess
import platform
import zipfile
from io import BytesIO

# 定义持久化存储文件的路径
COOKIE_FILE_PATH = 'ic_cookie.json'
DRIVER_DIR = r'.\driver'
EXCUTABLE_PATH = os.path.join(DRIVER_DIR, 'msedgedriver.exe')
Browser_Type = 'edge'

# 确保驱动目录存在
os.makedirs(DRIVER_DIR, exist_ok=True)

# 检查并下载匹配版本的Edge WebDriver
def check_and_download_edge_driver():
    if os.path.exists(EXCUTABLE_PATH):
        try:
            # 尝试获取当前驱动版本
            result = subprocess.run([EXCUTABLE_PATH, '--version'], capture_output=True, text=True)
            driver_version = result.stdout.split()[3]
            print(f"当前Edge WebDriver版本: {driver_version}")
        except:
            driver_version = None
    else:
        driver_version = None

    # 获取当前Edge浏览器版本
    try:
        if platform.system() == 'Windows':
            # 在Windows上获取Edge版本
            edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
            if os.path.exists(edge_path):
                result = subprocess.run([r'reg', 'query', r'HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon', '/v', 'version'], capture_output=True, text=True)
                browser_version = result.stdout.split()[-1]
                print(f"当前Edge浏览器版本: {browser_version}")
            else:
                print("未找到Edge浏览器")
                return False
        else:
            print("不支持的操作系统")
            return False
    except:
        print("无法获取Edge浏览器版本")
        return False

    # 如果没有驱动或版本不匹配，则下载
    if not driver_version or driver_version.split('.')[0] != browser_version.split('.')[0]:
        print(f"Edge WebDriver版本不匹配，需要下载版本 {browser_version.split('.')[0]}.*")

        try:
            # 构建下载URL
            download_url = f"https://msedgedriver.azureedge.net/{browser_version}/edgedriver_win64.zip"
            print(f"正在从 {download_url} 下载Edge WebDriver...")

            # 下载驱动
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # 解压缩并保存驱动
            with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extract('msedgedriver.exe', DRIVER_DIR)

            print(f"Edge WebDriver已成功下载并保存到 {EXCUTABLE_PATH}")
            return True
        except Exception as e:
            print(f"下载Edge WebDriver失败: {e}")
            print("请手动下载匹配版本的Edge WebDriver:")
            print(f"1. 访问 https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/")
            print(f"2. 下载与您的Edge版本 {browser_version} 匹配的WebDriver")
            print(f"3. 将驱动程序解压到 {DRIVER_DIR} 目录")
            return False
    else:
        print("Edge WebDriver版本匹配")
        return True



def login():
    # 检查并下载匹配版本的Edge WebDriver
    if not check_and_download_edge_driver():
        print("WebDriver准备失败，无法继续登录")
        return None
    
    # 检查是否有持久化的 ic-cookie 和 pid
    if os.path.exists(COOKIE_FILE_PATH):
        with open(COOKIE_FILE_PATH, 'r') as file:
            cookie_data = json.load(file)
            iccookie = cookie_data.get('ic-cookie')
            pid = cookie_data.get('pid')
        
        if iccookie and pid:
            # 检测 ic-cookie 是否有效
            headers = {
                "Cookie": f"ic-cookie={iccookie}",
            }
            response = requests.get('http://10.12.162.181/ic-web/auth/userInfo', headers=headers)
            response_json = response.json()

            if response_json['code'] == 0 and response_json['data']['pid'] == pid:
                # print("从文件中读取 ic-cookie 并验证有效")
                return iccookie
            else:
                # print("ic-cookie 无效，删除旧的 cookie 文件并重新登录")
                os.remove(COOKIE_FILE_PATH)

    # 使用 selenium 获取 cookies
    try:
        driver = get_driver(Browser_Type)
        
    except Exception as e:
        print(f"无法启动浏览器驱动: {e}")
        return None
    driver.get('http://10.12.162.181/')  # 打开目标网站
    
    # 循环获取 cookies 直到得到为止
    cookies = []
    flag = False
    while True:
        cookies = driver.get_cookies()
        if cookies:
            for cookie in cookies:
                if cookie['name'] == 'ic-cookie':
                    flag = True
                    iccookie = cookie['value']
                    break
            if flag:
                break
        time.sleep(1)

    # 关闭浏览器
    driver.quit()

    # 发送 GET 请求获取 JSON 数据
    headers = {
        "Cookie": f"ic-cookie={iccookie}",
    }
    response = requests.get('http://10.12.162.181/ic-web/auth/userInfo', headers=headers)
    response_json = response.json()

    if response_json['code'] == 0:
        pid = response_json['data']['pid']
        # 将获取到的 ic-cookie 和 pid 持久化存储到文件中
        cookie_data = {
            'ic-cookie': iccookie,
            'pid': pid
        }
        with open(COOKIE_FILE_PATH, 'w') as file:
            json.dump(cookie_data, file, ensure_ascii=False, indent=4)
        # print("已将 ic-cookie 和 pid 存储到文件中")
    else:
        # 如果获取用户信息失败，删除文件并重新登录
        os.remove(COOKIE_FILE_PATH)
        return login()

    return iccookie


def get_driver(browser_type='edge'):
    if browser_type.lower() == 'chrome':
        service = ChromeService(executable_path=EXCUTABLE_PATH)
        return Chrome(service=service)
    elif browser_type.lower() == 'firefox':
        service = FirefoxService(executable_path=EXCUTABLE_PATH)
        return Firefox(service=service)
    elif browser_type.lower() == 'safari':
        service = SafariService(executable_path=EXCUTABLE_PATH)
        return Safari(service=service)
    else:  # default to edge
        service = EdgeService(executable_path= EXCUTABLE_PATH)
        return Edge(service=service)
