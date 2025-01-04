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
    "sysKind": 1,#房间预约
    "appAccNo": 0,#预约主账号
    "resvBeginTime": "0",
    "resvEndTime": "0",
    "resvMember": [],#预约成员
    "resvDev": [],#预约设备
}

def find_devid_by_symbol(symbol):
    # 读取 roomdata.json 文件
    with open('roomdata.json', 'r', encoding='utf-8') as file:
        room_data = json.load(file)

    # 遍历房间数据，查找匹配的房间
    for room in room_data['rooms']:
        if symbol == room['roomName']:
            # print(f"找到房间：{room['roomName']}")
            return room['roomId']

    # 如果没有找到匹配的房间，返回 None
    return None

def fill_payload(iccookie):
    # 发送 GET 请求获取用户数据
    headers['Cookie'] = f"ic-cookie={iccookie}"
    response = requests.get('http://10.12.162.181/ic-web/auth/userInfo', headers=headers)
    userinfo = response.json()
    payload["resvMember"] = [userinfo["data"]["accNo"]]#包含自己

    while True:
        room = input("请输入预约房间号：")
        resvDev = find_devid_by_symbol(room)
        if resvDev is None:
            print("房间号不存在！")
        else:
            break
    while True:
        member = input("请输入除自己以外的预约成员学号,输入0退出：")
        if member == '0':
            break
        else:
            response = requests.get(f'http://10.12.162.181/ic-web/account/getMembers?key={member}&page=1&pageNum=10', headers=headers)
            response = response.json()
            payload["resvMember"].append(response['data'][0]['accNo'])
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
                response = requests.post("http://10.12.162.181/ic-web/reserve/delete", headers=headers , json={"uuid": uuid})
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
