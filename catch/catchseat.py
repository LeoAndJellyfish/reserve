import requests
import json
import os
headers = {
    "Cookie": f"ic-cookie=******",#ic-cookie保密
}
def catch_inf():
    url = "http://10.12.162.181/ic-web/seatMenu"
    response = requests.get(url)
    response_json = response.json()
    # print(response_json)
    seatkind = []
    for i in response_json['data']:
        for j in i['children']:
            for k in j['children']:
                rdata = {
                    'location': i['name'],
                    'kindId0': j['id'],
                    'kindName0': j['name'],
                    'kindId': k['id'],
                    'kindName': k['name']
                }
                seatkind.append(rdata)  # 直接添加新的子列表
    print(seatkind)
    seats = []
    for i in seatkind:
        print(f"正在获取{i['kindId']}的座位信息...")
        response = requests.get(f"http://10.12.162.181/ic-web/reserve?roomIds={i['kindId']}&resvDates=20250102&sysKind=8", headers=headers)#日期改成当天日期
        response_json = response.json()
        print(response_json)
        for j in response_json['data']:
            rdata = {
                'seatId': j['devId'],
                'seatName': j['devName'],
                'kindId': i['kindId'],
                'kindName': i['kindName'],
                'location': i['location']
            }
            seats.append(rdata)  # 直接添加新的子列表
    with open('seatdata.json', 'w') as file:
        json.dump({'seats': seats}, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    catch_inf()