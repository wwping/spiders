import tkinter
from tkinter import(Toplevel, Frame, LabelFrame, Message, messagebox,
                    Text, Entry, Button, ttk, Label, scrolledtext, INSERT, END, BOTH, LEFT, RIGHT, Checkbutton, IntVar, StringVar)
from tkinter.filedialog import askdirectory
import os
import subprocess
import threading
import tkinter.messagebox
sep = os.sep


class Change:
    def __init__(self):
        self.path = None

        ''''''

        top = Toplevel()
        top.title('转码')
        w = 300
        h = 300
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        # 计算 x, y 位置
        x = (ws/2) - (w/2)
        top.geometry('%dx%d+%d+%d' % (w, h, x, 100))

        ''''''

        frm1 = LabelFrame(top, width=300, height=100,
                          text='操作', labelanchor='nw')
        frm1.pack(side='top', fill='x', padx='20', pady='5')

        clupValue = IntVar()
        clipButton = Checkbutton(
            frm1, text="完成后打开文件夹", onvalue=1, offvalue=0, height=1, variable=clupValue)
        clipButton.pack(side='left', expand='yes', fill=None)
        clupValue.set(1)

        closeValue = IntVar()
        clipButton = Checkbutton(
            frm1, text="完成后关闭界面", onvalue=1, offvalue=0, height=1, variable=closeValue)
        clipButton.pack(side='right', expand='no', fill=None)
        closeValue.set(1)

        ''''''

        frm11 = LabelFrame(top, width=300, height=100,
                           text='转码设置', labelanchor='nw')
        frm11.pack(side='top',  padx='20', pady='5')

        originExt = StringVar()
        cmb = ttk.Combobox(frm11, textvariable=originExt, width=10)
        cmb.pack(side='left',  padx='20', pady='5')
        cmb['values'] = ('avi', 'mov', '3gp', 'wav', 'rmvb', 'mp4')
        originExt.set('mov')

        Label(frm11, text='转到').pack(
            side='left', fill='x', expand='yes',  padx='5', pady='5')

        toExt = StringVar()
        cmb = ttk.Combobox(frm11, textvariable=toExt, width=10)
        cmb.pack(side='left',  padx='20', pady='5')
        cmb['values'] = ('avi', 'mov', '3gp', 'wav', 'rmvb', 'mp4')
        toExt.set('mp4')
        ''''''

        frm2 = LabelFrame(top, width=300, height=100,
                          text='文件夹', labelanchor='nw')
        frm2.pack(side='top', fill='x', padx='20', pady='5')

        path = StringVar(frm2, value='download')
        inputPath = Entry(frm2, bd=0, textvariable=path, state='readonly')
        inputPath.pack(side='left')
        path.set('请选择文件夹')

        Button(frm2, bd=1, bg=None, text='选择文件夹',
               command=self.selectPath).pack(side='right')

        frm3 = LabelFrame(top, width=300, height=100,
                          text='提示', labelanchor='nw')
        frm3.pack(side='top', fill='x', padx='20', pady='5')

        tipsText = StringVar()
        tips = Label(frm3, text="未开始", textvariable=tipsText)
        tips.pack(side='top')
        tipsText.set('未开始')

        progressText = StringVar()
        progress = Label(frm3, text="0/0", textvariable=progressText)
        progress.pack(side='top')
        progressText.set('0/0')

        ''''''

        self.top = top
        self.tipsText = tipsText
        self.progressText = progressText
        self.inputPath = inputPath
        self.path = path
        self.clupValue = clupValue
        self.closeValue = closeValue
        self.originExt = originExt
        self.toExt = toExt

        self.files = []

        top.mainloop()

    def selectPath(self):
        path_ = askdirectory()
        if path_ and os.path.exists(path_):
            self.path.set(path_.replace('/', sep).replace('\\', sep))
            self.findMP4()

            t = threading.Thread(target=self.change)
            t.setDaemon(True)
            t.start()

    def change(self):
        length = len(self.files)
        self.progressText.set(f'0/{length}')
        toext_ = self.toExt.get()
        index = 1
        if length > 0:
            for file in self.files:
                self.tipsText.set(f'{index} 正在转码...')

                arr = file.split('.')
                arr[-1] = toext_
                imgPath = '.'.join(arr)
                child = subprocess.Popen(
                    f'ffmpeg -loglevel error -i "{file}" "{imgPath}" -y', shell=True)
                child.wait()

                self.progressText.set(f'{index}/{length}')

                index += 1

            self.tipsText.set(f'转码完成')
            tkinter.messagebox.showinfo('提示', '完成！！！')
            if self.clupValue.get() == 1:
                os.system(f'start explorer {self.path.get()}')
            if self.closeValue.get() == 1:
                self.top.destroy()
        else:
            tkinter.messagebox.showinfo('提示', '没找到任何文件')

    def findMP4(self):
        self.files = []
        path_ = self.path.get()
        oroginext_ = self.originExt.get()
        for root, dirs, files in os.walk(path_):  # path 为根目录

            for file in files:
                if file[-3:] == oroginext_:
                    self.files.append(f'{path_}{sep}{file}')
