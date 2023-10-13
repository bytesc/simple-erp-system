import datetime
import math


class MpsObj:
    def __init__(self, pname, require, deadline, index):
        self.pname = pname
        self.require = require
        self.deadline = deadline
        self.index = index


ans = []
MPS_output_que = []
MPS_obj_que = []

MPS_que_index = 0
ans_index = 0


def add(pname, require, deadline):
    global time
    global MPS_obj_que
    global MPS_que_index
    global ans_index

    if pname != '' and require != '' and deadline != '':
        time = 0

        deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d').date()
        MPS_obj_que.append(MpsObj(pname, require, deadline, MPS_que_index))
        MPS_output_que.append([pname, require, deadline, MPS_que_index])
        MPS_que_index = MPS_que_index + 1  # 录入一次就+1
        ans_index = MPS_que_index

        MPS_obj_que.sort(key=lambda item: item.deadline)


time = 0
rest_list = [0]


def show_result():
        global ans_index
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
        sql_state="""
            SELECT inventory."父物料名称", inventory."子物料名称", supply."调配方式", inventory."构成数", 
            supply."损耗率", store."工序库存",store."资材库存",supply."作业提前期",inventory."配料提前期",
            inventory."供应商提前期" 
            FROM inventory,supply,store 
            WHERE inventory."子物料名称"=supply."名称" AND inventory."子物料名称"=store."物料名称";
        """
        sql_res = connect(sql_state)
        print(sql_res)

        r=sql_res[0]
        for it in sql_res:
            if it[0] == '' or it[0] is None:
                r = BinaryTree(it)  # 找到根节点

        def tree_build(treenode):
            for it in sql_res:
                if it[0] == treenode.key[1]:
                    s = BinaryTree(it)
                    treenode.insert(s)
                    tree_build(s)
            return treenode

        r = tree_build(r)


        def sl_dfs(aim, number, treenode, rest, end_time):
            global ans_index
            if treenode.key[1] == aim:
                if number > rest:
                    treenode.need = number - rest
                    rest = 0
                start_time = end_time - datetime.timedelta(days=treenode.key[7] + treenode.key[8] + treenode.key[9])
                if number <= rest:
                    rest = rest - number
                    treenode.need = 0

                ans_index += 1
                ans.append([treenode.key[1], treenode.need, treenode.key[2], start_time, end_time])

            """开始日期=下一级项目的结束日期"""
            end_time = end_time - datetime.timedelta(days=treenode.key[7] + treenode.key[8] + treenode.key[9])

            if treenode.next1 == None:
                 return rest
            else:
                number1 = math.ceil(number * treenode.next1.key[3] / (1 - treenode.next1.key[4]))
                rest = sl_dfs(aim, number1, treenode.next1, rest, end_time)

                if treenode.next2 == None:
                    return rest
                else:
                    number2 = math.ceil(number * treenode.next2.key[3] / (1 - treenode.next2.key[4]))

                    rest = sl_dfs(aim, number2, treenode.next2, rest, end_time)

                    if treenode.next3 == None:
                        return rest
                    else:
                        number3 = math.ceil(number * treenode.next3.key[3] / (1 - treenode.next3.key[4]))

                        rest = sl_dfs(aim, number3, treenode.next3, rest, end_time)

                        if treenode.next4 == None:
                            return rest
                        else:
                            number4 = math.ceil(number * treenode.next4.key[3] / (1 - treenode.next4.key[4]))

                            rest = sl_dfs(aim, number4, treenode.next4, rest, end_time)
            return rest

        name_list=[]
        supply = connect('select supply."名称" FROM supply')
        for item in supply:
            name_list.append(item[0])

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
            rest_list = [rest_dfs(name_list[0], r), rest_dfs(name_list[1], r), rest_dfs(name_list[2], r),
                         rest_dfs(name_list[3], r), rest_dfs(name_list[4], r), rest_dfs(name_list[5], r),
                         rest_dfs(name_list[6], r)]

        for x in MPS_obj_que:
            if x.pname == '眼镜':  # 对应的树根节点为r
                time = time + 1
                ans_index = ans_index + 1

                for y in range(7):
                    rest_list[y] = sl_dfs(name_list[y], x.require, r, rest_list[y], x.deadline)
            elif x.pname == '镜框':  # 对应的树根节点为r.next1
                time = time + 1
                ans_index = ans_index + 1

                for y in range(1, 6):
                    rest_list[y] = sl_dfs(name_list[y], x.require, r.next1, rest_list[y], x.deadline)



###############################################################################################





def clear():
    global MPS_que_index
    global ans_index
    global MPS_obj_que
    MPS_que_index=0
    ans_index=0
    global MPS_output_que
    MPS_output_que=[]
    MPS_obj_que = []
    global ans
    ans=[]


from connectdb import connect
supply_available=[]
sql_res = connect('select DISTINCT inventory."父物料名称" from inventory')
for item in sql_res:
    if item[0]!="" and item[0] is not None:
        supply_available.append(item)



#########################################################################################33
#####################################################################

func_index = 0
func_obj_que=[]
func_que=[]
func_ans_que=[]
class collect():
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.outp = [name, '=']

def add_func_x(name):
    global func_obj_que
    global func_index
    if name != '':
        for it in func_obj_que:
            it.outp = [it.name, '=']
        func_obj_que.append(collect(name, func_index))
        func_que.append(name)
        func_index += 1


def show_func():
    global func_ans_que
    func_ans_que=[]
    global func_index
    global func_obj_que
    bom = connect("select * from bom")

    for x in func_obj_que:
        flag_x_exist = 0
        """先寻找对应的序号"""
        for y in bom:
            if y[4] == x.name:
                num = y[0]
                flag_x_exist = 1
        if flag_x_exist == 0:
            x.outp.clear()
            x.outp.append("未找到对应的变量")
            continue

        # 再拼接对应变量
        flag_x_source = 0
        for y in bom:
            if y[3] == num:
                flag_x_source = 1
                if flag_x_exist == 0:
                    x.outp.append('+')
                x.outp.append(y[4])
                print(y[3], num, x.outp)
                flag_x_exist = 0
        if flag_x_source == 0:
            x.outp = ["未找到资产流入来源"]
    for x in func_obj_que:
        s = ''.join(x.outp)
        func_ans_que.append(x.name+"  "+s)


def func_clear():
    global func_index
    global func_obj_que
    global func_que
    global func_ans_que
    func_index = 0
    func_obj_que = []
    func_que = []
    func_ans_que = []


##############################################################################################33

from fastapi import FastAPI, Form  # 导入FastAPI和Form
from starlette.requests import Request  # 导入Request类
from starlette.templating import Jinja2Templates  # 导入Jinja2Templates类

# from erpsys import add, show_result, clear, MPS_output_que, ans

app = FastAPI()  # 创建FastAPI应用实例
templates = Jinja2Templates(directory="templates")  # 创建Jinja2Templates实例，并指定模板目录为"templates"


@app.get("/")
async def root(request: Request):  # 定义根路由处理函数，接受Request对象作为参数
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,
                                                     "que": MPS_output_que,
                                                     "supply_available":supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


@app.post("/erp/")
async def root(request: Request,
                    pname: str = Form("default"),
                    num: str = Form("0"),
                    date: str = Form("2002-11-13")):  # 定义根路由下的POST请求处理函数，接受Request对象和表单数据作为参数
    print(pname, num, date)  # 打印表单数据
    add(pname, int(num), date)  # 调用add函数处理表单数据
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,
                                                     "que": MPS_output_que,
                                                     "supply_available":supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


@app.get("/show/")
async def root(request: Request):  # 定义/show/路由的GET请求处理函数，接受Request对象作为参数
    show_result()
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,
                                                     "que": MPS_output_que,
                                                     "supply_available":supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量

@app.get("/clear/")
async def root(request: Request):  # 定义/clear/路由的GET请求处理函数，接受Request对象作为参数
    clear()  # 调用clear函数
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,
                                                     "que": MPS_output_que,
                                                     "supply_available":supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


#########################################################################################

sql_x_res = connect("""SELECT bom."变量名" from bom 
WHERE bom."变量名" IS NOT NULL and bom."变量名" != ''""")
x_avilable=[]
for item in sql_x_res:
    x_avilable.append(item[0])

@app.get("/func/")
async def root(request: Request):
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": func_que,
                                                    "x_available":x_avilable})

@app.post("/func/")
async def root(request: Request,
            x=Form("")):
    add_func_x(x)
    print(func_que)
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": func_que,
                                                    "x_available":x_avilable})

@app.get("/func_show/")
async def root(request: Request):
    show_func()
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": func_ans_que,
                                                    "x_available":x_avilable})

@app.get("/func_clear/")
async def root(request: Request):
    func_clear()
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": func_que,
                                                    "x_available":x_avilable})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)  # 运行FastAPI应用，监听本地主机的8080端口