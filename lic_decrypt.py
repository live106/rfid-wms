
from Crypto.Cipher import AES
from Crypto.Util import Counter
from lic import *
from config import DATA_PATH

# 定义一个函数，使用AES算法和密钥解密license
def decrypt_license(encrypted_license, key):
    # 创建一个计数器对象
    ctr = Counter.new(128, initial_value=int.from_bytes(LIC_AES_IV, byteorder='big'))
    # 创建一个AES对象
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)
    # 解密并返回明文
    decrypted_license = aes.decrypt(encrypted_license)
    return decrypted_license

# 定义一个函数，验证license是否匹配设备mac地址
def verify_license():
    # 调用generate_license函数，根据mac地址生成license 
    license = generate_license() 
    # 调用read_key函数，从key.txt文件中读取密钥 
    # key = read_key() 
    # 打开license.txt文件，以读取模式 
    with open(f"{DATA_PATH}/license.txt", "rb") as f: 
        #读取文件内容，得到加密后的license字符串 
        encrypted_license = f.read() 
        # 关闭文件 
        f.close() 
    # 调用decrypt_license函数，使用AES算法和密钥解密license 
    decrypted_license = decrypt_license(encrypted_license, LIC_AES_KEY) 
    # 比较解密后的license和原始的license是否相等，返回布尔值 
    return decrypted_license == license.encode('utf-8')

if __name__ == '__main__':
    result = verify_license()
    # 打印验证结果 
    if result: 
        print("License is valid.") 
    else: 
        print("License is invalid.")