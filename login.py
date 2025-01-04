from selenium import webdriver
import time
import os
import requests
import json

# 定义持久化存储文件的路径
COOKIE_FILE_PATH = 'ic_cookie.json'

def login():
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
    driver = webdriver.Edge()  # 或指定合适的浏览器驱动
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
