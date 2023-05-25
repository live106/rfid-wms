import sys
import uuid

# 定义一个32字节的密钥
LIC_AES_KEY = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f' \
      b'\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'
# 设置iv为固定值, 一个16字节的随机初始化向量
LIC_AES_IV = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f'

# 定义一个函数，根据设备mac地址生成license
def generate_license(mac_address = None):
    if not mac_address:
        mac_address = get_mac_address()
    # 将mac地址转换为小写，并去掉冒号
    mac_address = mac_address.lower().replace(":", "")
    # 使用uuid模块的uuid5方法，根据mac地址和一个命名空间生成一个uuid对象
    license = uuid.uuid5(uuid.NAMESPACE_DNS, mac_address)
    # 将uuid对象转换为字符串，并去掉横线
    license = str(license).replace("-", "")
    # 返回license字符串
    return license

# # 定义一个函数，从key.txt文件中读取密钥
# def read_key():
#     # 打开key.txt文件，以二进制读取模式
#     with open("key.txt", "rb") as f:
#         # 读取文件内容，得到密钥字节串
#         key = f.read()
#         # 关闭文件
#         f.close()
#     # 返回密钥
#     return key

# 定义一个函数，获取当前设备的mac地址
def get_mac_address():
    # 使用uuid模块的getnode方法，获取当前设备的mac地址，返回一个整数
    mac_address = uuid.getnode()
    # 将整数转换为16进制字符串，并去掉开头的0x
    mac_address = hex(mac_address)[2:]
    # 在每两个字符之间插入冒号，得到标准格式的mac地址
    mac_address = ":".join([mac_address[i:i+2] for i in range(0, len(mac_address), 2)])
    # 返回mac地址字符串
    return mac_address

if __name__ == '__main__':
    mac_address = None
    if len(sys.argv) > 1: # check if there is an argument
        mac_address = sys.argv[1] # get the argument
        license = generate_license(mac_address) # pass it to the function
    else:
        license = generate_license() # use the default function
    if not mac_address:
        mac_address = get_mac_address()
    print(f'license for mac {mac_address} is {license}')