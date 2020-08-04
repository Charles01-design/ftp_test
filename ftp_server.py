"""
ｆｔｐ　文件服务器服务端
"""

from socket import *
from threading import Thread
import sys
from time import sleep
import os

# 全局变量
ADDR = ('0.0.0.0', 16999)
# 文件库的路径,后面加个/，因为子目录让用户自己去选择
FTP = '/home/wutan/FTP/'


def handle(c):
    # print(c.recv(1024)) #　测试代码，检测是否连接成功
    cls = c.recv(1024).decode()
    FTP_PATH = FTP + cls + '/'  # 跟目录拼接，最后再拼接一个/
    ftp = FtpServer(c, FTP_PATH)  # 创建对象,把套接字和文件途径作为参数
    while 1:
        data = c.recv(1024).decode()
        # print(FTP_PATH,':',data)  # 测试代码
        if not data or data[0] == 'Q':  # 除了Ｑ之外，客户端也有可能直接Ｃｔｒｌ　Ｃ，所以要加个条件
            return  # 结束线程只需要让函数结束
        elif data[0] == 'L':
            ftp.do_list()
        elif data[0] == 'G':
            data_list = data.split(' ')
            file_name = data_list[1]
            # print(FTP_PATH) # 测试路径是否正确
            ftp.do_get(file_name)
        elif data[0] == 'U':
            data_list = data.split(' ')
            file_name = data_list[-1]
            ftp.do_upload(file_name)


# 将客户端请求功能封装为类
class FtpServer:
    def __init__(self, connfd, FTP_PATH):
        self.connfd = connfd
        self.path = FTP_PATH

    def do_list(self):
        # 获取文件列表
        files = os.listdir(self.path)  # 文件函数里面有一个查看文件列表
        if not files:
            self.connfd.send('该文件类别为空')
        else:
            self.connfd.send(b'OK')
            sleep(0.1)  # 防止这边的沾包，而下面文件数量有时会很大，所以不要用睡眠处理

            fs = ''  # 人为添加消息边界
            for file in files:
                if file[0] != '.' and os.path.isfile(self.path+file):  # 只发送普通非隐藏文件，这里也是用文件常见操作函数
                    # self.connfd.send(file.encode())       # 直接发会沾包
                    fs += file + '\n'  # 把文件名放进这个fs里面，最后把fs发过去就好了
            self.connfd.send(fs.encode())
            # self.connfd.send(b'##')     # 作为对方停止接收的标志,此时不用了

    def do_get(self,path):
        # 判断文件是否存在，是则调用下载文件方法，没有则返回原因
        # if os.path.exists(path):
        #     self.connfd.send(b'OK')
        #     sleep(0.1)
        #     self.do_get_file(path)
        # else:
        #     self.connfd.send('文件不存在'.encode())
        try:
            fd = open(self.path+ path, 'rb')
        except Exception:
            self.connfd.send('文件不存在'.encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)

        # 发送文件内容
        while 1:
            data = fd.read(1024)
            if not data:
                sleep(0.1)
                self.connfd.send(b'##')
                fd.close()
                break
            self.connfd.send(data)

    def do_get_file(self,path):
        fr = open(path,'rb')
        while 1:
            print('开始传输')
            data = fr.read(1024)
            if not data:
                fr.close()
                break
            self.connfd.send(data)
        print('传输结束')

    def do_upload(self,file_name):
        if os.path.exists(self.path+file_name):
            self.connfd.send('文件已存在'.encode())
        else:
            self.connfd.send(b'OK')
            fd = open(self.path+file_name,'wb')
            print("开始下载")
            while 1:
                data = self.connfd.recv(1024)
                if data == '##'.encode():
                    fd.close()
                    break
                fd.write(data)
            print("下载成功")





# 网络搭建
def main():
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(3)

    print('Listen the port 12999')

    while 1:
        try:
            c, addr = s.accept()
        except KeyboardInterrupt:
            sys.exit('服务器退出')
        except Exception as e:
            print(e)
            continue

        print('连接的客户端为：', addr)

        t = Thread(target=handle, args=(c,))
        t.setDaemon(True)
        t.start()


if __name__ == "__main__":
    main()
