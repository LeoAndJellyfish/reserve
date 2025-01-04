import requests
from login import login

iccookie = login()
response = requests.get('http://10.12.162.181/ic-web/creditPunishRec/surPlus', headers={'Cookie': f"ic-cookie={iccookie}"})
response_json = response.json()
print(response_json['message'])
if response_json['code'] == 0:
    print(f"座位信用{response_json['data']['8']}")
    print(f"研讨室信用{response_json['data']['1']}")
response = requests.get('http://10.12.162.181/ic-web/creditRec/getOwn?page=1&pageNum=10', headers={'Cookie': f"ic-cookie={iccookie}"})
response_json = response.json()
if response_json['code'] == 0:
    print("最近十条信用记录：")
    print(response_json['message'])
    print(response_json['data'])