#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Lear.Li'

from PIL import Image  # 图片处理模块
import argparse
import sys
import os
import cv2
import pyprind


class CharFrame:

    ascii_char = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

    # 像素映射到字符
    def pixelToChar(self, luminance):
        return self.ascii_char[int(luminance/256*len(self.ascii_char))]

    # 将普通帧转为 ASCII 字符帧
    # limitSize 参数接受一个元组，表示图片的限宽限高。
    # fill 表示是否用空格填充图片宽度至限宽，wrap 表示是否在行末添加换行符
    def convert(self, img, limitSize=-1, fill=False, wrap=False):
        if limitSize != -1 and (img.shape[0] > limitSize[1] or img.shape[1] > limitSize[0]):
            img = cv2.resize(img, limitSize, interpolation=cv2.INTER_AREA)
        ascii_frame = ''
        blank = ''
        if fill:
            blank += ' '*(limitSize[0]-img.shape[1])
        if wrap:
            blank += '\n'
        for i in range(img.shape[0]): # shape 为元组 图片的（宽，高）
            for j in range(img.shape[1]):
                ascii_frame += self.pixelToChar(img[i,j])
            ascii_frame += blank
        return ascii_frame


'''
图片转字符画
'''

class I2Char(CharFrame):

    result = None

    def __init__(self, path, limitSize=-1, fill=False, wrap=False):
        self.genCharImage(path, limitSize, fill, wrap)

    def genCharImage(self, path, limitSize=-1, fill=False, wrap=False):

        # 给self.result 字符画字符串赋值
        # 命令行输入参数处理
        parser = argparse.ArgumentParser()

        parser.add_argument('file')  # 输入文件
        parser.add_argument('-o', '--output')  # 输出文件
        parser.add_argument('--width', type=int, default=80)  # 输出字符画宽
        parser.add_argument('--height', type=int, default=80)  # 输出字符画高

        # 获取参数
        args = parser.parse_args()

        IMG = args.file
        WIDTH = args.width
        HEIGHT = args.height
        OUTPUT = args.output

        # 转换的字符集合，共70个，可自己优化添加，越多越逼真，每个字符对应一种或者几种亮度
        ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

        # 将256灰度映射到70个字符上
        def get_char(r, g, b, alpha=256):
            # alpha 值为 0 的时候表示图片中该位置为空白
            if alpha == 0:
                return ' '
            length = len(ascii_char)
            # 把RGB色域转换成灰度图 ，使用权重
            gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
            # ascii_char有70个，把256个灰度值分成70组
            unit = (256.0 + 1) / length
            # 当前像素的灰度属于70个组中的哪个组
            return ascii_char[int(gray / unit)]

        if __name__ == '__main__':
            # 1.通过PiL模块加载一张图片到内存
            im = Image.open(IMG)
            # 2.设置图片的尺寸
            im = im.resize((WIDTH, HEIGHT), Image.NEAREST)
            txt = ""
            # 3.遍历提取图片中每行的像素的 RGB 值，调用 getchar 转成对应的字符
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    # 获取得到坐标 (j,i) 位置的 RGB 像素值（有的时候会包含 alpha 值），
                    # 返回的结果是一个元组，例如 (1,2,3) 或者 (1,2,3,0)
                    # 4.将所有的像素对应的字符拼接在一起成为一个字符串 txt
                    txt += get_char(*im.getpixel((j, i)))
                txt += '\n'
            # 5.打印输出字符串 txt
            print(txt)

            # 6.如果执行时配置了输出文件，将打开文件将 txt 输出到文件，如果没有，
            # 则默认输出到 output.txt 文件
            if OUTPUT:
                with open(OUTPUT, 'w') as f:
                    f.write(txt)
            else:
                with open("output.txt", 'w') as f:
                    f.write(txt)
        self.result = ''


    def show(self, stream = 2):
        if self.result is None:
            return
        if stream == 1 and os.isatty(sys.stdout.fileno()):
            self.streamOut = sys.stdout.write
            self.streamFlush = sys.stdout.flush
        elif stream == 2 and os.isatty(sys.stderr.fileno()):
            self.streamOut = sys.stderr.write
            self.streamFlush = sys.stderr.flush
        elif hasattr(stream, 'write'):
            self.streamOut = stream.write
            self.streamFlush = stream.flush
        self.streamOut(self.result)
        self.streamFlush()
        self.streamOut('\n')


'''
视频转字符画
'''

class V2Char(CharFrame):
    # charVideo ，这是一个列表，用来存放字符动画全部数据,一个元素代表一个frame数据
    charVideo = []
    # 播放的时间间隔 FPS = 30
    timeInterval = 0.033

    def __init__(self, path):
        if path.endswith('txt'):
            self.load(path)
        else:
            self.genCharVideo(path)

    # 从视频文件转为字符动画
    # 调用 genCharVideo() 方法将视频转化为字符动画存放到属性 charVideo 里：
    def genCharVideo(self, filepath):
        self.charVideo = []
        # 方法读取视频文件，生成的对象我们赋值给 cap
        cap = cv2.VideoCapture(filepath)
        # cap.get(3) 和 cap.get(4) 分别返回视频的宽高信息，
        # cap.get(5) 则返回视频的帧率FPS，cap.get(7) 返回视频的总帧数
        # 存放播放时间间隔，用来让之后播放字符动画的帧率与原视频相同
        self.timeInterval = round(1/cap.get(5), 3)
        nf = int(cap.get(7))
        print('正在转换每一帧成字符画，请稍后...')
        # 使用这个生成器进行迭代会自然在终端中输出进度条
        for i in pyprind.prog_bar(range(nf)):
            # cap.read() 读取视频的下一帧，其返回一个两元素的元组，第一个元素为 bool 值，
            # 指示帧是否被正确读取，第二个元素为2维度数组numpy对象 ，其存放的便是帧的数据
            rawFrame = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2GRAY)
            frame = self.convert(rawFrame, os.get_terminal_size(), fill=True)
            self.charVideo.append(frame)
        cap.release()

    # charVideo 中的字符动画数据导出来，方便下次读取播放
    def export(self, filepath):
        if not self.charVideo:
            return
        with open(filepath,'w') as f:
            for frame in self.charVideo:
                # 加一个换行符用以分隔每一帧
                f.write(frame + '\n')
    # 从txt中导入字符动画，方便播放
    def load(self, filepath):
        self.charVideo = []
        # 一行即为一帧
        for i in open(filepath):
            self.charVideo.append(i[:-1])
    # 播放字符动画的方法
    def play(self, stream = 1):
        # Bug:
        # 光标定位转义编码不兼容 Windows
        # 转义编码       行动
        # \033[l;cH 把光标移到第l行，第c列。
        # \033[nA   把光标向上移动n行。
        # \033[nB   把光标向下移动n行。
        # \033[nC   把光标向前移动n个字符。
        # \033[nD   把光标向后移动n个字符。
        # \033[2J   清空屏幕，把光标移到左上角（第零行，第零列）。
        # \033[K    清空从光标位置到当前行末的内容。
        # \033[s    存储当前光标位置。
        # \033[u    唤醒之前存储的光标位置
        if not self.charVideo:
            return
        if stream == 1 and os.isatty(sys.stdout.fileno()):
            self.streamOut = sys.stdout.write
            self.streamFlush = sys.stdout.flush
        elif stream == 2 and os.isatty(sys.stderr.fileno()):
            self.streamOut = sys.stderr.write
            self.streamFlush = sys.stderr.flush
        elif hasattr(stream, 'write'):
            self.streamOut = stream.write
            self.streamFlush = stream.flush

        old_settings = None
        breakflag = None
        # 获得标准输入的文件描述符
        fd = sys.stdin.fileno()

        def getChar():
            global breakflag
            global old_settings
            # 保存标准输入的属性
            old_settings = termios.tcgetattr(fd)
            # 设置标准输入为原始模式
            tty.setraw(sys.stdin.fileno())
            # 读取一个字符
            ch = sys.stdin.read(1)
            breakflag = True if ch else False

        # 创建线程
        getchar = threading.Thread(target=getChar)
        # 设置为守护线程
        getchar.daemon = True
        # 启动守护线程
        getchar.start()
        # 输出的字符画行数
        rows = len(self.charVideo[0])//os.get_terminal_size()[0]
        for frame in self.charVideo:
            # 接收到输入则退出循环
            if breakflag is True:
                break
            self.streamOut(frame)
            self.streamFlush()
            time.sleep(self.timeInterval)
            # 共 rows 行，光标上移 rows-1 行回到开始处
            self.streamOut('\033[{}A\r'.format(rows-1))
        # 恢复标准输入为原来的属性
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        # 光标下移 rows-1 行到最后一行，清空最后一行
        self.streamOut('\033[{}B\033[K'.format(rows-1))
        # 清空最后一帧的所有行（从倒数第二行起）
        for i in range(rows-1):
            # 光标上移一行
            self.streamOut('\033[1A')
            # 清空光标所在行
            self.streamOut('\r\033[K')
        info = 'User interrupt!\n' if breakflag else 'Finished!\n'
        self.streamOut(info)

