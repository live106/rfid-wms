import http.client
import json
import time
from database import get_rfid_reader_config
import threading

stop_async_inventory_event = threading.Event()  # Define stop_async_inventory_event as a threading.Event object

def call_api(address, port, path, request_params):
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    jstr = json.dumps(request_params)
    try:
        conn = http.client.HTTPConnection(address, port)
        conn.request('POST', f'/moduleapi/{path}', jstr, headers)
        response = conn.getresponse()
        data = b''
        chunk = response.read(1024)
        while chunk:
            data += chunk
            chunk = response.read(1024)
        conn.close()
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        error_message = str(e)
        error_data = {'err_code': -1, 'err_string': error_message}
        return error_data

def start(address, port, request_params, retries):
    while retries > 0:
        try:
            response_data = call_api(address, port, 'startasyncinventory', request_params)
            if response_data['err_code'] == 0:
                print("Successfully started async inventory.")
                return response_data
            else:
                print(response_data['err_string'])
                retries -= 1
                time.sleep(1)
        except Exception as e:
            error_message = str(e)
            print(error_message)
            pass
    print("Error: Maximum number of retries reached.")
    return None

def async_get_epc_list(epc_list, duration_ref):
    config = get_rfid_reader_config()
    address = config['address']
    port = config['port']
    duration = config['inventory_duration']
    consecutive_count = config['consecutive_count']
    retries = config['inventory_api_retries']
    antennas = [int(a) for a in config['antennas'].split(',')]

    call_api(address, port, 'stopasyncinventory', {})
    start(address, port, {'antennas': antennas}, retries)

    current_consecutive_count = 0
    start_time = time.time()
    while current_consecutive_count < consecutive_count and time.time() - start_time < duration and not stop_async_inventory_event.is_set():
        try:
            response_data = call_api(address, port, 'getasynctags', {})
            if response_data['err_code'] == 0:
                result = response_data['result']
                new_epc_list = [tag['epc'] for tag in result]
                new_epc_list = list(set(new_epc_list))
                if new_epc_list == epc_list:
                    current_consecutive_count += 1
                else:
                    current_consecutive_count = 0
                    epc_list.extend(new_epc_list)
                    temp_list = list(epc_list)
                    epc_list.clear()
                    epc_list.extend(set(temp_list))  # remove duplicates                
                    print('epc_list: ', epc_list)
            else:
                print(response_data['err_string'])
        except Exception as e:
            error_message = str(e)
            print(error_message)
            pass
        duration_ref[0] = duration - (time.time() - start_time)
        time.sleep(1)
    retries_left = retries
    while retries_left > 0:
        try:
            response_data = call_api(address, port, 'stopasyncinventory', {})
            if response_data['err_code'] == 0:
                print("Successfully stopped async inventory.")
                return epc_list
            else:
                print(response_data['err_string'])
                retries_left -= 1
                time.sleep(1)
        except Exception as e:
            error_message = str(e)
            print(error_message)
            pass
    print("Error: Maximum number of retries reached.")
    return None

def sync_get_epc_list(epc_list):
    config = get_rfid_reader_config()
    address = config['address']
    port = config['port']
    duration = config['inventory_duration'] * 100
    retries = config['inventory_api_retries']
    antennas = [int(a) for a in config['antennas'].split(',')]
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    request_params = {'antennas': antennas, 'timeout': duration}
    response_data = call_api(address, port, 'syncinventory', request_params)
    if response_data['err_code'] == 0:
        result = response_data['result']
        epc_list = [tag['epc'] for tag in result]
        epc_list = list(set(epc_list))
        return epc_list
    else:
        print(response_data['err_string'])
        retries_left = retries
        while retries_left > 0:
            time.sleep(1)
            response_data = call_api(address, port, 'syncinventory', request_params)
            if response_data['err_code'] == 0:
                result = response_data['result']
                epc_list = [tag['epc'] for tag in result]
                epc_list = list(set(epc_list))
                return epc_list
            else:
                print(response_data['err_string'])
                retries_left -= 1
        print("Error: Maximum number of retries reached.")
        return None    

'''
开始异步盘存

startasyncinventory

antennas	Number数组	是	盘存使用的天线，每个元素代表一个天线id
tag_filter	TagFilter对象	否	过滤条件，如果需要只盘存满足某些数据特征的标签可以加入此对象
bank_data_option	BankDataOpt对象	否	如果需要在盘存中读某一个bank的数据可以加入此对象

例子1
开始异步盘存，使用天线1，2
请求对象
{
-"antennas": [
1,
2
]
}
     
例子2
开始异步盘存，使用天线1，2，但只盘存epc码以1110开头的标签
  
请求对象
{
-"antennas": [
1,
2
],
-"tag_filter": {
"bank": 1,
"start_bit": 32,
"mask": "1110",
"match": true
}
}
   
例子3
开始异步盘存，使用天线1，2，但只盘存epc码以1110开头的标签，并且读取bank2从0块开始的6个块数据
  
请求对象
{
-"antennas": [
1,
2
],
-"tag_filter": {
"bank": 1,
"start_bit": 32,
"mask": "1110",
"match": true
},
-"bank_data_option": {
"bank": 2,
"start_block": 0,
"block_count": 6,
"access_password": "00000000"
}
}
     
以上示例的响应对象
{
"reader_name": "silion_reader/192.168.1.100",
"op_type": "startasyncinventory",
"err_code": 0,
"err_string": "ok"
}
'''

'''
获取盘存标签

getasynctags

TagInfo对象数组	标签信息

请求对象
{ }
  
响应对象
{
"reader_name": "silion_reader/192.168.1.100",
"op_type": "getasynctags",
"err_code": 0,
"err_string": "ok",
-"result": [
-{
"epc": "E20041453116009820603EC6",
"bank_data": "",
"antenna": 1,
"read_count": 30,
"protocol": 5,
"rssi": -63,
"firstseen_timestamp": 0,
"lastseen_timestamp": 0
},
-{
"epc": "E20041453116011620703E7F",
"bank_data": "",
"antenna": 2,
"read_count": 1,
"protocol": 5,
"rssi": -77,
"firstseen_timestamp": 0,
"lastseen_timestamp": 0
}
]
}
'''

'''
停止异步盘存

stopasyncinventory

请求对象
{ }
  
响应对象
{
"reader_name": "silion_reader/192.168.1.100",
"op_type": "stopasyncinventory",
"err_code": 0,
"err_string": "ok"
}
'''

'''
同步盘存标签

syncinventory


成员名称	类型	是否必须	描述
antennas	Number数组	是	盘存使用的天线，每个元素代表一个天线id
timeout	Number	是	盘存的时间长度
tag_filter	TagFilter对象	否	过滤条件，如果需要只盘存满足某些数据特征的标签可以加入此对象
bank_data_option	BankDataOpt对象	否	如果需要在盘存中读某一个bank的数据可以加入此对象

例子1
使用天线1，2盘存300ms
  
请求对象
{
-"antennas": [
1,
2
],
"timeout": 300
}
    
例子2
使用天线1，2盘存300ms，但只盘存epc码以1110开头的标签
  
请求对象
{
-"antennas": [
1,
2
],
"timeout": 300,
-"tag_filter": {
"bank": 1,
"start_bit": 32,
"mask": "1110",
"match": true
}
}
    
以上示例的响应对象
{
"reader_name": "silion_reader/192.168.1.100",
"op_type": "syncinventory",
"err_code": 0,
"err_string": "ok",
-"result": [
-{
"epc": "E20041453116009820603EC6",
"bank_data": "",
"antenna": 1,
"read_count": 30,
"protocol": 5,
"rssi": -63,
"firstseen_timestamp": 0,
"lastseen_timestamp": 0
},
-{
"epc": "E20041453116011620703E7F",
"bank_data": "",
"antenna": 2,
"read_count": 1,
"protocol": 5,
"rssi": -77,
"firstseen_timestamp": 0,
"lastseen_timestamp": 0
}
]
}
        
例子3
使用天线1，2盘存300ms，但只盘存epc码以1110开头的标签，并且读取bank2从0块开始的6个块数据
  
请求对象
{
-"antennas": [
1,
2
],
"timeout": 300,
-"tag_filter": {
"bank": 1,
"start_bit": 32,
"mask": "1110",
"match": true
},
-"bank_data_option": {
"bank": 2,
"start_block": 0,
"block_count": 6,
"access_password": "00000000"
}
}
   
响应对象
{
"reader_name": "silion_reader/192.168.1.100",
"op_type": "syncinventory",
"err_code": 0,
"err_string": "ok",
-"result": [
-{
"epc": "E20041453116009820603EC6",
"bank_data": "E2003412012EF800091D3EC6",
"antenna": 1,
"read_count": 30,
"protocol": 5,
"rssi": -63,
"firstseen_timestamp": 0,
"lastseen_timestamp": 0
},
-{
"epc": "E20041453116011620703E7F",
"bank_data": "E20034120133F800091D3E7F",
"antenna": 2,
"read_count": 1,
"protocol": 5,
"rssi": -77,
"firstseen_timestamp": 0,
"lastseen_timestamp": 0
}
]
}
'''