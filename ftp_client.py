from socket import *
import sys
from time import sleep

# 具体功能封装为类
class FtpClient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b'L')  # 发送请求，Ｌ表示请求列表的协议
        # 等待回复
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':  # ＯＫ表示请求成功
            # while 1:      #　不再循环接收，只收一次
            data = self.sockfd.recv(4096)
            # if data == b'##':
            #     break
            print(data.decode())
        else:
            print(data)  # 打印失败原因

    def do_quit(self):  # 客户端退出
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit("谢谢使用")

    def do_get(self,file_name):
        com = 'G %s'%file_name
        self.sockfd.send(com.encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            # print(data)     # 测试是否收到
            self.do_get_file(file_name)
        else:
            print(data)

    def do_get_file(self,file_name):    # 完成下载操作
        fw = open(file_name,'wb')
        print("开始下载")
        while 1:
            data = self.sockfd.recv(1024)
            if data == b'##':       # 对方没法发空格过来
                fw.close()
                break
            fw.write(data)
        print("下载成功")

    def do_upload(self,file_name):
        try:
            fd = open(file_name,'rb')
        except:
            print('没有该文件')
            return

        file_name = file_name.split('/')[-1]    # 去掉文件的路径
        com = 'U %s'%file_name
        self.sockfd.send(com.encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            # fd = open(file_name,'rb') # 换到前面了
            print("开始上传")
            while 1:
                data = fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send('##'.encode())
                    fd.close()
                    break
                self.sockfd.send(data)
            print("上传成功")
        else:
            print(data)



def request(sockfd):
    ftp = FtpClient(sockfd)
    while 1:
        print('\n========命令选项========')
        print('======== list ========')
        print('======= get file =======')
        print('===== upload file =====')
        print('======== quit ========')
        print('======================')

        cmd = input('请输入命令：')
        if cmd.strip() == 'list':  # strip去除两边空格
            ftp.do_list()
        elif cmd.strip() == 'quit':
            ftp.do_quit()
        elif cmd[:3] == 'get':
            file_name = cmd.strip().split(' ')[-1]  # 去掉两边空格，取出文件名称
            ftp.do_get(file_name)
        elif cmd[:6] == 'upload':
            file_name = cmd.strip().split(' ')[-1]
            ftp.do_upload(file_name)



# 网络连接
def main():
    # 服务器地址
    ADDR = ('127.0.0.1', 16999)
    s = socket()
    try:
        s.connect(ADDR)
    except Exception as e:
        print('连接服务器失败')
    else:
        print('''
            **********************
            Data    File    Image
            **********************
        ''')
        cls = input("请输入文件种类：")
        if cls not in ['Data', 'File', 'Image']:
            print('Sorry input Error!!')
            return
        else:
            s.send(cls.encode())
            request(s)  # 发送具体请求


if __name__ == "__main__":
    main()
