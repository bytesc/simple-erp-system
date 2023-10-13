from asyncio.windows_events import NULL
from contextlib import nullcontext
import tkinter as tk
from tkinter import ttk
import pymysql

root = tk.Tk()
root.title('资产负债计算')
root.geometry('550x570+90+50')

bl = tk.StringVar()

"""上面布局"""
T_frame = tk.Frame(root)
T_frame.pack(side=tk.TOP,anchor=tk.N,padx=5,pady=5)

r_frame=tk.LabelFrame(T_frame,padx=10,pady=5,borderwidth='0')
r_frame.pack(side=tk.LEFT)

tk.Label(r_frame,text='请输入要计算的变量名').pack(anchor=tk.W)
entry_port = ttk.Entry(r_frame,width='15',textvariable=bl).pack(anchor=tk.W)


"""-----------------------------------------------------------------------"""

from connectdb import connect

class collect():
    def __init__(self,name,index):
        self.name=name
        self.index=index
        self.outp = [name,'=']

"""刷新调配计划"""
def delButton(tree):
    global bl
    x=tree_view.get_children()
    for item in x:
        tree.delete(item)
    bl.set('')


flg = 0
MPS_obj_que = []
MPS_que_index = 0
"""录入"""
def lr():
    global flg
    global MPS_obj_que
    global MPS_que_index

    name = bl.get()
    if name != '':
        for it in arrdata:
            it.outp=[it.name,'=']

        flg =1
        arrdata.append(collect(name,index))
        delButton(tree_view)

        for it in arrdata:
            s = ["第",0,"次录入:",it.name]
            s[1]= it.MPS_que_index + 1
            tree_view.insert('', it.MPS_que_index, values=(s, ''))
        index = index + 1


def show():
    global flg
    if flg == 1:
        results=connect("select * from bom")
        index2 = MPS_que_index

        for x in MPS_obj_que:
            flg2 = 0
            """先寻找对应的序号"""
            for y in results:
                if y[4] == x.name:
                    num =y[0]
                    flg2 = 1
            if flg2 == 0:           #可能要找的变量不存在
                x.outp.clear()
                x.outp.append("未找到对应的变量")
                continue

            """再拼接对应的变量"""
            flg3 = 0        #判断是否有来源
            for y in results:
                if y[3] == num:
                    flg3 = 1
                    if flg2 ==0:
                        x.outp.append('+')
                    x.outp.append(y[4])
                    print(y[3],num,x.outp)
                    flg2 = 0
            if flg3 == 0:
                x.outp=["未找到资产流入来源"]
        
        delButton(tree_view)
        for x in MPS_obj_que:
            s=''.join(x.outp)
            n = ["第", x.MPS_que_index + 1, "次录入:", x.name]
            tree_view.insert('',index2,values=(n,s))
    flg = 0
        
                



def restart():
    global flg
    global MPS_obj_que
    global MPS_que_index

    delButton(tree_view)
    flg = 0
    arrdata = []
    index = 0
"""-----------------------------------------------------------------------"""

"""中间布局"""
M_frame = tk.Frame(root)
M_frame.pack(side=tk.TOP,anchor=tk.N,padx=5,pady=10)

submit_button = tk.Button(M_frame,text='录入',command=lr,width='10')
submit_button.pack(side=tk.LEFT,anchor=tk.N,padx=10)

submit_button = tk.Button(M_frame,text='提交',command=show,width='10')
submit_button.pack(side=tk.LEFT,anchor=tk.N,padx=10)

submit_button = tk.Button(M_frame,text='restart',command=restart,width='10')
submit_button.pack(side=tk.LEFT,anchor=tk.N,padx=10)

"""下面布局"""
B_frame = tk.Frame(root)
B_frame.pack(side=tk.TOP,anchor=tk.N,padx=10,pady=10)


columns = ("lr","gs")
columns_values = ("录入","公式")
tree_view = ttk.Treeview(B_frame,height=20,show='headings',columns=columns)
tree_view.pack(side=tk.LEFT,fill=tk.Y,expand=True)
tree_view.column('lr',width='100',anchor='center')
tree_view.column('gs',width='400',anchor='center')
tree_view.heading('lr',text='录入：')
tree_view.heading('gs',text='公式：')

text_bar = tk.Scrollbar(B_frame,command=tree_view.yview)
text_bar.pack(side=tk.RIGHT,fill=tk.Y)
tree_view.config(yscrollcommand=text_bar.set)   #将滚动条链接到输出框

root.mainloop()