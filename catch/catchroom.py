import requests
import json
import os
headers = {
    "Cookie": f"ic-cookie=******",#ic-cookie保密
}
def catch_inf():
    url = "http://10.12.162.181/ic-web/roomMenu"
    response = requests.get(url)
    response_json = response.json()
    roomkind = []
    for i in response_json['data']:
        rdata = {
            'kindId': i['kindId'],
            'kindName': i['kindName']
        }
        roomkind.append(rdata)  # 直接添加新的子列表
    rooms = []
    for i in roomkind:
        print(f"正在获取{i['kindId']}的房间信息...")
        response = requests.get(f"http://10.12.162.181/ic-web/reserve?sysKind=1&resvDates=20250102&page=1&pageSize=10&kindIds={i['kindId']}", headers=headers)#日期改成当天日期
        response_json = response.json()
        print(response_json)
        for j in response_json['data']:
            rdata = {
                'roomId': j['devId'],
                'roomName': j['devName'],
                'kindId': i['kindId'],
                'kindName': i['kindName']
            }
            rooms.append(rdata)  # 直接添加新的子列表
    with open('roomdata.json', 'w') as file:
        json.dump({'rooms': rooms}, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    catch_inf()