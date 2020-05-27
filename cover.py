import tkinter
from tkinter import(Toplevel, Frame, LabelFrame, Message, messagebox,
                    Text, Entry, Button, ttk, Label, scrolledtext, INSERT, END, BOTH, LEFT, RIGHT, Checkbutton, IntVar, StringVar)
from tkinter.filedialog import askdirectory
import os
import subprocess
import threading
import tkinter.messagebox
sep = os.sep


class Cover:
    def __init__(self):
        self.path = None

        ''''''

        top = Toplevel()
        top.title('生成封面')
        w = 300
        h = 200
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        # 计算 x, y 位置
        x = (ws/2) - (w/2)
        top.geometry('%dx%d+%d+%d' % (w, h, x, 100))

        ''''''

        clupValue = IntVar()
        clipButton = Checkbutton(
            top, text="完成后打开文件夹", onvalue=1, offvalue=0, height=1, variable=clupValue)
        clipButton.pack(side='top', expand='no', fill=None)
        clupValue.set(1)

        closeValue = IntVar()
        clipButton = Checkbutton(
            top, text="完成后关闭界面", onvalue=1, offvalue=0, height=1, variable=closeValue)
        clipButton.pack(side='top', expand='no', fill=None)
        closeValue.set(1)

        Button(top, bd=1, bg=None, text='选择文件夹',
               command=self.selectPath).pack(side='top')

        path = StringVar(top, value='download')
        inputPath = Entry(top, bd=0, textvariable=path, state='readonly')
        inputPath.pack(side='top')
        path.set('请选择文件夹')

        progressText = StringVar()
        progress = Label(top, text="请选择文件夹", textvariable=progressText)
        progress.pack(side='top')
        progressText.set('0/0')

        ''''''

        self.top = top
        self.progressText = progressText
        self.inputPath = inputPath
        self.path = path
        self.clupValue = clupValue
        self.closeValue = closeValue

        self.files = []

        top.mainloop()

    def selectPath(self):
        path_ = askdirectory()
        if path_ and os.path.exists(path_):
            self.path.set(path_.replace('/', sep).replace('\\', sep))
            self.findMP4()

            t = threading.Thread(target=self.born)
            t.setDaemon(True)
            t.start()

    def born(self):
        length = len(self.files)
        self.progressText.set(f'0/{length}')
        index = 1
        if length > 0:
            for file in self.files:
                arr = file.split('.')
                arr[-1] = 'jpg'
                imgPath = '.'.join(arr)
                child = subprocess.Popen(
                    f'ffmpeg -loglevel error -i "{file}" -f image2 -frames:v 1 "{imgPath}" -y', shell=True)
                child.wait()

                self.progressText.set(f'{index}/{length}')

                index += 1
            tkinter.messagebox.showinfo('提示', '生成完成！！！')
            if self.clupValue.get() == 1:
                os.system(f'start explorer {self.path.get()}')
            if self.closeValue.get() == 1:
                self.top.destroy()
        else:
            tkinter.messagebox.showinfo('提示', '没找到任何视频')

    def findMP4(self):
        self.files = []
        path_ = self.path.get()
        for root, dirs, files in os.walk(path_):  # path 为根目录

            for file in files:
                if file[-3:] == 'mp4':
                    self.files.append(f'{path_}{sep}{file}')
