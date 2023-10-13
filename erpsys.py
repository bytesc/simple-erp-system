import datetime
import math
import operator


ans = []
MPS_output_que = []

class MPS:
    def __init__(self, pname, require, deadline, index):
        self.pname = pname
        self.require = require
        self.deadline = deadline
        self.index = index
        if pname == "眼镜":
            self.mark = deadline - datetime.timedelta(days=1)
        elif pname == "镜框":
            self.mark = deadline


"""录入数据"""
arrdata = []
index = 0
index2 = 0
flg = 0


def add(pname, require, deadline):
    """点击 录入 则会重置time,从而使得重新提交后的rest()按照最开始的计算"""
    global time
    """控制show不可连点,只有在录入之后可以点击一次"""
    global flg

    global arrdata
    global sortdata
    global index
    global index2

    if pname != '' and require != '' and deadline != '':
        time = 0
        flg = 1
        deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d').date()
        arrdata.append(MPS(pname, require, deadline, index))
        MPS_output_que.append([pname, require, deadline, index])
        index = index + 1  # 录入一次就+1
        index2 = index

        cmpfun = operator.attrgetter('index')
        arrdata.sort(key=cmpfun)


        cal(arrdata)


"""计算哪个计划最先执行,再show()里面会调用"""
sortdata = []


def cal(arrdata):
    global sortdata
    sortdata = arrdata  # arrdata的内容不变
    for x in range(0, index):
        for y in range(x + 1, index):
            c = sortdata[y].mark - sortdata[x].mark
            c = c.days
            if c < 0:
                tmp = sortdata[x]
                sortdata[x] = sortdata[y]
                sortdata[y] = tmp
            elif c == 0:
                if sortdata[y].index < sortdata[x].index:
                    tmp = sortdata[x]
                    sortdata[x] = sortdata[y]
                    sortdata[y] = tmp


"""重置按钮"""


def restart():
    global time
    global index
    global index2
    global arrdata
    global sortdata
    global flg
    time = 0
    index = 0
    index2 = 0
    flg = 0
    arrdata = []
    sortdata = []


time = 0  # 用来记录第几次录入的计划，并且第一次的计划才会用到数据库的库存值
rest_list = [0]


def show_result():
    global flg
    if flg == 1:
        global index2
        global time
        global rest_list

        """树定义"""
        class BinaryTree:
            def __init__(self, rootObj):
                self.key = list(rootObj)
                self.need = 0
                self.next1 = None
                self.next2 = None
                self.next3 = None
                self.next4 = None

            def insert(self, newNode):
                if self.next1 == None:
                    self.next1 = newNode
                elif self.next2 == None:
                    self.next2 = newNode
                elif self.next3 == None:
                    self.next3 = newNode
                elif self.next4 == None:
                    self.next4 = newNode

        from connectdb import connect
        results = connect("select * from compose")
        print(results)
        """树建立"""
        for it in results:
            if it[0] == '' or it[0] is None:
                r = BinaryTree(it)  # 找到根节点

        def tree_build(treenode):
            for it in results:
                if it[0] == treenode.key[1]:
                    s = BinaryTree(it)
                    treenode.insert(s)
                    tree_build(s)
            return treenode

        r = tree_build(r)

        """深度遍历"""

        def sl_dfs(aim, number, treenode, rest, time):
            global index2
            if treenode.key[1] == aim:
                if number > rest:
                    treenode.need = number - rest
                    rest = 0
                stime = time - datetime.timedelta(days=treenode.key[7] + treenode.key[8] + treenode.key[9])
                if number <= rest:
                    rest = rest - number
                    treenode.need = 0

                index2 += 1
                ans.append([treenode.key[1], treenode.need, treenode.key[2], stime, time])

            """开始日期=下一级项目的结束日期"""
            time = time - datetime.timedelta(days=treenode.key[7] + treenode.key[8] + treenode.key[9])

            if treenode.next1 == None:
                 return rest
            else:
                number1 = math.ceil(number * treenode.next1.key[3] / (1 - treenode.next1.key[4]))
                rest = sl_dfs(aim, number1, treenode.next1, rest, time)

                if treenode.next2 == None:
                    return rest
                else:
                    number2 = math.ceil(number * treenode.next2.key[3] / (1 - treenode.next2.key[4]))

                    rest = sl_dfs(aim, number2, treenode.next2, rest, time)

                    if treenode.next3 == None:
                        return rest
                    else:
                        number3 = math.ceil(number * treenode.next3.key[3] / (1 - treenode.next3.key[4]))

                        rest = sl_dfs(aim, number3, treenode.next3, rest, time)

                        if treenode.next4 == None:
                            return rest
                        else:
                            number4 = math.ceil(number * treenode.next4.key[3] / (1 - treenode.next4.key[4]))

                            rest = sl_dfs(aim, number4, treenode.next4, rest, time)
            return rest

        name_list1 = ['眼镜', '镜框', '螺钉', '镜架', '镜腿', '鼻托', '镜片']
        """寻找剩余库存"""

        def rest_dfs(name, treenode):
            if treenode == None:
                return 0
            if name == treenode.key[1]:
                return treenode.key[5] + treenode.key[6]
            else:
                s1 = rest_dfs(name, treenode.next1)
                s2 = rest_dfs(name, treenode.next2)
                s3 = rest_dfs(name, treenode.next3)
                s4 = rest_dfs(name, treenode.next4)
                return max(s1, s2, s3, s4)

        """剩余库存表"""
        if time == 0:
            rest_list = [rest_dfs(name_list1[0], r), rest_dfs(name_list1[1], r), rest_dfs(name_list1[2], r),
                         rest_dfs(name_list1[3], r), rest_dfs(name_list1[4], r), rest_dfs(name_list1[5], r),
                         rest_dfs(name_list1[6], r)]


        for x in sortdata:
            if x.pname == '眼镜':  # 对应的树根节点为r
                time = time + 1
                index2 = index2 + 1

                for y in range(7):
                    rest_list[y] = sl_dfs(name_list1[y], x.require, r, rest_list[y], x.deadline)  # 每一次都会改变剩余物料的值
            elif x.pname == '镜框':  # 对应的树根节点为r.next1
                time = time + 1
                index2 = index2 + 1
                for y in range(1, 6):
                    rest_list[y] = sl_dfs(name_list1[y], x.require, r.next1, rest_list[y], x.deadline)
    flg = 0


###############################################################################################


def clear():
    global index
    global index2
    global flg
    index=0
    index2=0
    flg=0
    global MPS_output_que
    MPS_output_que=[]
    global ans
    ans=[]

######################################################################################3

from fastapi import FastAPI, Form  # 导入FastAPI和Form
from starlette.requests import Request  # 导入Request类
from starlette.templating import Jinja2Templates  # 导入Jinja2Templates类

# from erpsys import add, show_result, clear, MPS_output_que, ans

app = FastAPI()  # 创建FastAPI应用实例
templates = Jinja2Templates(directory="templates")  # 创建Jinja2Templates实例，并指定模板目录为"templates"


@app.get("/")
async def root(request: Request):  # 定义根路由处理函数，接受Request对象作为参数
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans, "que": MPS_output_que})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


@app.post("/erp/")
async def root_post(request: Request,
                    pname: str = Form("default"),
                    num: str = Form("0"),
                    date: str = Form("2002-11-13")):  # 定义根路由下的POST请求处理函数，接受Request对象和表单数据作为参数
    print(pname, num, date)  # 打印表单数据
    add(pname, int(num), date)  # 调用add函数处理表单数据
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,"que": MPS_output_que})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


@app.get("/show/")
async def root_post(request: Request):  # 定义/show/路由的GET请求处理函数，接受Request对象作为参数
    show_result()  # 调用show函数
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,"que": MPS_output_que})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


@app.get("/clear/")
async def root_post(request: Request):  # 定义/clear/路由的GET请求处理函数，接受Request对象作为参数
    clear()  # 调用clear函数
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans, "que": MPS_output_que})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)  # 运行FastAPI应用，监听本地主机的8080端口