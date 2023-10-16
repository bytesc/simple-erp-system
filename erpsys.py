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


def add(pname, require, deadline):
    global time
    global MPS_obj_que
    global MPS_que_index

    if pname != '' and require != '' and deadline != '':
        time = 0

        deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d').date()
        MPS_obj_que.append(MpsObj(pname, require, deadline, MPS_que_index))
        MPS_output_que.append([pname, require, deadline, MPS_que_index])
        MPS_que_index = MPS_que_index + 1  # 录入一次就+1

        MPS_obj_que.sort(key=lambda item: item.deadline)


def show_result():

        global ans
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

        compose = []
        for i in sql_res:
            compose.append(list(i))
        print(compose)

        def refresh_store(item, store_1, store_2):
            for i in compose:
                if i[1] == item[1]:
                    i[5] -= store_1
                    i[6] -= store_2

        def main_dfs(item, need_num, ans, end_time):
            need_num = math.ceil(need_num/(1-item[4]))  # 损耗
            if need_num <= item[5]+item[6]:
                if need_num <= item[5]:  # 工序够用
                    start_time = end_time - datetime.timedelta(days=item[7])
                    ans.append([item[1], 0, item[2], start_time, end_time])
                    refresh_store(item, need_num, 0)
                else:  # 工序不够，资材库存够用
                    start_time = end_time - datetime.timedelta(days=item[7] + item[8])
                    ans.append([item[1], need_num - item[5], item[2], start_time, end_time])
                    refresh_store(item, item[5], need_num - item[5])
            else:  # 工序和资材库存都不够用
                start_time = end_time - datetime.timedelta(days=item[7] + item[8] + item[9])
                ans.append([item[1], need_num - item[5] - item[6], item[2], start_time, end_time])
                refresh_store(item, item[5], item[6])

            child_items=[]
            for child in compose:
                if child[0]==item[1]:
                    child_items.append(child)

            if len(child_items)==0:
                return
            else:
                for child in child_items:
                    main_dfs(child,need_num*child[3],ans,start_time)

        for mps in MPS_obj_que:
            for item in compose:
                if mps.pname == item[1]:
                    main_dfs(item, mps.require, ans, mps.deadline)

def refresh_db():
    pass

###############################################################################################



def clear():
    global MPS_que_index
    global MPS_obj_que
    global MPS_output_que
    MPS_que_index=0
    MPS_output_que=[]
    MPS_obj_que = []
    global ans
    ans=[]


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

from connectdb import connect
supply_available=[]
sql_res = connect('select DISTINCT inventory."父物料名称" from inventory')
for item in sql_res:
    if item[0]!="" and item[0] is not None:
        supply_available.append(item)

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