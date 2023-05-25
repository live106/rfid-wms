# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
from Crypto.Util import Counter
from lic import *
from config import DATA_PATH

# 定义一个函数，使用AES算法和密钥加密license
def encrypt_license(license, key):
    # 创建一个计数器对象
    ctr = Counter.new(128, initial_value=int.from_bytes(LIC_AES_IV, byteorder='big'))
    # 创建一个AES对象
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)
    # 加密并返回初始化向量和密文
    encrypted_license = aes.encrypt(license.encode('utf-8'))
    return encrypted_license

# 定义一个函数，用于生成license文件和key文件
def generate_license_file(license):
    # with open(f"{DATA_PATH}/license_org.txt", "w") as f:
    #     f.write(license)
    #     f.close()
    # 调用generate_key函数，随机生成一个密钥
    # key = read_key()
    # 调用encrypt_license函数，使用AES算法和密钥加密license
    encrypted_license = encrypt_license(license, LIC_AES_KEY)
    # 打开一个文件，以写入模式
    with open(f"{DATA_PATH}/license.txt", "wb") as f:
        # 将加密后的license写入文件
        f.write(encrypted_license)
        # 关闭文件
        f.close()
    # 打印提示信息
    print("License file generated successfully.")

if __name__ == '__main__':
    # 调用generate_license函数，根据mac地址生成license
    license = generate_license()
    generate_license_file(license)
