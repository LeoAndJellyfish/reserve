import requests
import json
import time
from login import login

# 全局配置
headers = {
    "Cookie": "ic-cookie=NA",
}

payload = {
    "sysKind": 8,  # 座位预约
    "appAccNo": 0,  # 预约主账号
    "resvBeginTime": "0",
    "resvEndTime": "0",
    "resvMember": [],  # 预约成员
    "resvDev": [],  # 预约设备
}

def get_user_info(iccookie):
    """获取用户信息"""
    headers['Cookie'] = f"ic-cookie={iccookie}"
    response = requests.get('http://10.12.162.181/ic-web/auth/userInfo', headers=headers)
    return response.json()

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

def get_seat_input():
    """获取座位号输入"""
    while True:
        room = input("请输入预约座位号：")
        resvDev = find_devid_by_symbol(room)
        if resvDev is None:
            print("座位号不存在！")
        else:
            return resvDev

def get_time_input(time_type):
    """获取时间输入"""
    while True:
        time_str = input(f"请输入预约{time_type}时间（格式：2025-01-03 13:20:00）：")
        try:
            time.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            return time_str
        except ValueError:
            print("时间格式错误！")

def main():
    """主程序入口"""
    iccookie = login()
    userinfo = get_user_info(iccookie)
    
    # 获取用户输入
    resvDev = get_seat_input()
    begin_time = get_time_input("开始")
    end_time = get_time_input("结束")
    
    # 填充payload
    payload.update({
        "appAccNo": userinfo["data"]["accNo"],
        "resvMember": [userinfo["data"]["accNo"]],
        "resvDev": [resvDev],
        "resvBeginTime": begin_time,
        "resvEndTime": end_time
    })
    
    # 发送请求
    while True:
        if send_post_request() == 0:
            break
        else:
            time.sleep(60)

if __name__ == "__main__":
    main()
