# reserve
某大学图书馆座位预约系统

## 使用方法

### 信息获取模块
1. 运行 `python catchroom.py` 获取图书馆房间信息并保存到roomdata.json
2. 运行 `python catchseat.py` 获取图书馆座位信息并保存到seatdata.json

### 预约模块
1. 运行 `python room.py` 预约图书馆房间
2. 运行 `python seat.py` 预约图书馆座位

### 信用查询模块
1. 运行 `python credit.py` 查询用户信用分及记录

## 环境准备
1. 安装Python 3.x环境
2. 安装项目依赖：`pip install selenium requests`
如需更换浏览器，需下载对应浏览器的WebDriver并将其放入driver文件夹下并修改login.py中的EXCUTABLE_PATH和Browser_Type。
默认支持Chrome，Firefox，Edge，Safari。

## 注意事项
1. 请确保已安装Python 3.x环境和所有依赖
2. 运行前请检查网络连接
