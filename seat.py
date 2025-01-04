import requests
import json
import time
from login import login

# 配置请求头
headers = {
    "Cookie": "ic-cookie=NA",
}

# 配置 JSON 请求体
payload = {
    "sysKind": 8,#座位预约
    "appAccNo": 0,#预约主账号
    "resvBeginTime": "0",
    "resvEndTime": "0",
    "resvMember": [],#预约成员
    "resvDev": [],#预约设备
}

def find_devid_by_symbol(symbol):
    # 读取 seatdata.json 文件
    with open('seatdata.json', 'r', encoding='utf-8') as file:
        seat_data = json.load(file)

    # 遍历座位数据，查找匹配的座位
    for seat in seat_data['seats']:
        if symbol == seat['seatName']:
            # print(f"找到座位：{seat['seatName']}")
            return seat['seatId']

    # 如果没有找到匹配的座位，返回 None
    return None

def fill_payload(iccookie):
    # 发送 GET 请求获取用户数据
    headers['Cookie'] = f"ic-cookie={iccookie}"
    response = requests.get('http://10.12.162.181/ic-web/auth/userInfo', headers=headers)
    userinfo = response.json()
    
    while True:
        room = input("请输入预约座位号：")
        resvDev = find_devid_by_symbol(room)
        if resvDev is None:
            print("座位号不存在！")
        else:
            break
    while True:
        begin_time = input("请输入预约开始时间（格式：2025-01-03 13:20:00）：")
        try:
            time.strptime(begin_time, '%Y-%m-%d %H:%M:%S')
            payload["resvBeginTime"] = begin_time
            break
        except ValueError:
            print("时间格式错误！")
    while True:
        end_time = input("请输入预约结束时间（格式：2025-01-03 14:00:00）：")
        try:
            time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            payload["resvEndTime"] = end_time
            break
        except ValueError:
            print("时间格式错误！")

    # 填充 payload
    payload["appAccNo"] = userinfo["data"]["accNo"]
    payload["resvMember"] = [userinfo["data"]["accNo"]]
    payload["resvDev"] = [resvDev]

# 发送 POST 请求的函数
def send_post_request():
    try:
        response = requests.post("http://10.12.162.181/ic-web/reserve", headers=headers, json=payload)

        # 打印状态码
        print(f"Status Code: {response.status_code}")

        response_json = response.json()

        # 打印解压后的响应内容
        # print("Response JSON:")
        # print(json.dumps(response_json, indent=4, ensure_ascii=False))
        if response_json['code'] == 0:
            print("预约成功！")
            uuid = response_json['data']['uuid']
            # print(f"预约编号：{uuid}")
            inn =input("是否删除预约？（输入 y 确认删除）：")
            if inn == 'y' or inn == 'Y':
                response = requests.post(f"http://10.12.162.181/ic-web/reserve/delete", headers=headers , json={"uuid": uuid})
                if response.status_code == 200:
                    print("删除成功！")
                else:
                    print("删除失败！")
            return 0
        else:
            print("预约失败！")
            print(response_json['message'])
            return 1

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return 1

# 登录获取 cookies
iccookie = login()
fill_payload(iccookie)

while True:
    # 发送 POST 请求
    if send_post_request() == 0:
        break
    else:
        time.sleep(60)  # 60秒 = 1分钟
