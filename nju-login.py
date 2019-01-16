# 参考： https://www.polarxiong.com/archives/Python-%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E6%A0%A1%E5%9B%AD%E7%BD%91%E8%87%AA%E5%8A%A8%E7%99%BB%E5%BD%95%E8%84%9A%E6%9C%AC-V2-0.html

import urllib.request
import urllib.parse
import json
import time
import os
import base64
import sys
import codecs

login_url = 'http://p.nju.edu.cn/portal_io/login'  # 登录post的URL
logout_url = 'http://p.nju.edu.cn/portal_io/logout'  # 登出post的URL
info_url = 'http://p.nju.edu.cn/portal_io/getinfo'  # 获取用户信息URL
info_name = 'info.ini'  # 存储账号密码

class NJU_Login():

    def __init__(self):  # 获取保存的账号密码，若文件不存在则创建文件
        self.info_path = os.path.join(os.path.split(os.path.realpath(sys.argv[0]))[0], info_name)
        if os.path.exists(self.info_path):
            with open(self.info_path, 'r') as f:
                self.id = self.decrypt(f.readline().strip())
                self.pw = self.decrypt(f.readline().strip())

    def set_id_pw(self, id, pw):  # 设置账号密码并存入文件
        self.id = id
        self.pw = pw
        with open(self.info_path, 'w') as f:
            f.write('%s\n%s' % (self.encrypt(id), self.encrypt(pw)))

    def login(self):  # 登录接口
        data = urllib.parse.urlencode({  # 转换post的form并编码
            'username': self.id,
            'password': self.pw
        }).encode('utf-8')
        post = urllib.request.urlopen(url=login_url, data=data)
        return json.loads(post.read().decode('utf-8'))  # 获得登录信息

    def encrypt(self, s):  # 加密账号密码
        return base64.b32encode(base64.b64encode(s.encode('utf-8'))).decode('utf-8')

    def decrypt(self, s):  # 解密账号密码
        return base64.b64decode(base64.b32decode(s)).decode('utf-8')

    def logout(self):  # 登出接口
        post = urllib.request.Request(url=logout_url, method='POST')
        con = urllib.request.urlopen(post)
        return json.loads(con.read().decode('utf-8'))

    def get_info(self):  # 获取用户信息
        # urlopen()不能指定post，这里用Request()
        post = urllib.request.Request(url=info_url, method='POST')
        con = urllib.request.urlopen(post)
        info = json.loads(con.read().decode('utf-8'))  # 获得用户信息
        if info['reply_code'] == 0:
            text = ('姓名：%s\n'
                    '学号：%s\n'
                    '接入区域：%s\n'
                    '服务类别：%s\n'
                    '网费余额：%.2f元\n')
            text_real = (info['userinfo']['fullname'],  # 与text配合
                         info['userinfo']['username'],
                         info['userinfo']['area_name'],
                         info['userinfo']['service_name'],
                         info['userinfo']['balance'] / 100)
            return text % text_real
        else:
            return -1

    def first_time_login(self):  # 登录后至获取用户信息存在2秒左右延时，需要单独处理
        time.sleep(1)  # 延时1秒
        count = 0  # 重复尝试计数
        while 1:
            info = self.get_info()
            if info == -1:
                count += 1
                time.sleep(0.5)  # 延时0.5秒再次尝试
                if count == 4:  # 重复尝试4次，若仍获取不到，则放弃
                    return "无法获取登录信息！"
            else:
                return info

    def connect(self):  # 登录
        ln = self.login()
        if ln['reply_code'] == 1:  # 首次登录成功
            return ln['reply_msg'] + '\n' + self.first_time_login()
        elif ln['reply_code'] == 6:  # 已经登录成功，但重复尝试登录
            return ln['reply_msg'] + '\n\n' + self.get_info()
        else:  # 其他情况，提示错误
            return ln['reply_msg']

    def disconnect(self):  # 登出
        count = 0  # 重复尝试计数
        while 1:
            logout = self.logout()
            if self.get_info() == -1:  # 如果不能获取到用户信息，则登出成功
                return logout['reply_msg']
            else:
                count += 1
                time.sleep(0.5)
                if count == 6:  # 重复尝试6次
                    return '未知原因，下线失败！'

if __name__ == '__main__':
    nju = NJU_Login()
    log_path = os.path.join(os.path.split(os.path.realpath(sys.argv[0]))[0], 'log')
    with codecs.open(log_path, 'w', encoding='utf8') as fout:
        text = nju.connect()
        fout.write(text)
        print(text)
        time.sleep(10)