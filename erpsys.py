import copy
import datetime
import math
import asyncio

mutex_for_store = asyncio.Lock()  # 只允许一个修改库存
mutex_for_mps = asyncio.Lock()


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


async def add_mps(pname, require, deadline):
    global time
    global MPS_obj_que
    global MPS_que_index
    await mutex_for_mps.acquire()
    try:
        if pname != '' and require != '' and deadline != '':
            time = 0

            deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d').date()
            MPS_obj_que.append(MpsObj(pname, require, deadline, MPS_que_index))
            MPS_output_que.append([pname, require, deadline, MPS_que_index])
            MPS_que_index = MPS_que_index + 1  # 录入一次就+1

            MPS_obj_que.sort(key=lambda item: item.deadline)
    finally:
        mutex_for_mps.release()


class Node:
    def __init__(self, father, child, way, comp_num,
                 loss_rate, store_1, store_2, adv_work, adv_make, adv_supply):
        self.father = father
        self.child = child
        self.way = way  # 调配方式
        self.comp_num = comp_num
        self.loss_rate = loss_rate
        self.store_1 = store_1  # 工序库存
        self.store_2 = store_2  # 资材库存
        self.adv_work = adv_work  # 作业提前期
        self.adv_make = adv_make  # 配料提前期
        self.adv_supply = adv_supply  # 供应商提前期
        self.depth = -1  # 节点深度
        self.child_depth = -1  # 子树的深度


async def show_result():
    await mutex_for_store.acquire()
    await mutex_for_mps.acquire()
    try:
        global ans
        sql_state = """
                SELECT inventory."父物料名称", inventory."子物料名称", supply."调配方式", inventory."构成数", 
                supply."损耗率", store."工序库存",store."资材库存",supply."作业提前期",inventory."配料提前期",
                inventory."供应商提前期" 
                FROM inventory,supply,store 
                WHERE inventory."子物料名称"=supply."名称" AND inventory."子物料名称"=store."物料名称";
            """
        from connectdb import select_from_db
        sql_res = await select_from_db(sql_state)
        # print(sql_res)

        compose = []
        for i in sql_res:
            compose.append(Node(*i))

        def mark_depth(item, deep):  # 标记所有节点深度
            child_items = []
            for i in compose:
                if i.child == item.child and i.father == item.father:
                    if i.depth == -1:
                        i.depth = deep
                    else:  # 存在子父相同但层次不同的节点
                        i2 = copy.deepcopy(i)  # 新建节点
                        i2.depth = deep
                        compose.append(i2)

            for child in compose:
                if child.father == item.child and (child.depth == -1 or child.depth == deep+1):
                    child_items.append(child)
            if len(child_items) == 0:
                return
            else:
                for child in child_items:
                    mark_depth(child, deep+1)

        def mark_child_depth(item):  # 标记所有节点子树最大深度
            child_items = []
            for child in compose:
                if child.father == item.child and child.depth == item.depth+1:
                    child_items.append(child)

            if len(child_items) == 0:
                item.child_depth = item.depth
                return
            else:
                for child in child_items:
                    mark_child_depth(child)
                for child in child_items:
                    item.child_depth = max(item.child_depth, child.child_depth)

        def refresh_store(item, store_1, store_2):  # 刷新库存
            for i in compose:
                if i.child == item.child:
                    i.store_1 -= store_1
                    i.store_2 -= store_2

        def main_dfs(item, need_num, ans, end_time):
            if need_num <= 0:
                return
            need_num = math.ceil(need_num/(1-item.loss_rate))  # 损耗
            real_need_num = need_num
            if need_num <= item.store_1+item.store_2:  # 库存够
                if need_num <= item.store_1:  # 工序够用
                    start_time = end_time - datetime.timedelta(days=item.adv_supply)
                    ans.append([item.child, 0, item.way, start_time, end_time])
                    real_need_num = 0
                    refresh_store(item, need_num, 0)
                else:  # 工序不够，但加上资材库存够用
                    start_time = end_time - datetime.timedelta(days=item.adv_supply + item.adv_make)
                    ans.append([item.child, need_num - item.store_1, item.way, start_time, end_time])
                    real_need_num = 0
                    refresh_store(item, item.store_1, need_num - item.store_1)
            else:  # 库存不够（工序和资材库存加起来都不够用）
                start_time = end_time - datetime.timedelta(days=item.adv_supply + item.adv_make + item.adv_work)
                ans.append([item.child, need_num - item.store_2 - item.store_1, item.way, start_time, end_time])
                real_need_num = need_num - item.store_1 - item.store_2
                refresh_store(item, item.store_1, item.store_2)

            child_items = []
            for child in compose:
                if child.father == item.child and child.depth == item.depth+1:
                    child_items.append(child)

            if len(child_items) == 0:
                return
            else:
                child_items.sort(key=lambda item: -item.child_depth)  # 按子树深度倒序，先遍历深的
                for child in child_items:
                    main_dfs(child, real_need_num*child.comp_num, ans, start_time)

        for item in compose:  # 找根节点计算深度
            if item.father is None:
                mark_depth(item, 0)
                mark_child_depth(item)

        for mps in MPS_obj_que:  # 遍历 mps 队列计算结果
            for item in compose:
                if mps.pname == item.child:
                    main_dfs(item, mps.require, ans, mps.deadline)

        await refresh_db(compose)
    finally:
        mutex_for_store.release()
        mutex_for_mps.release()


async def refresh_db(compose):
    from connectdb import exec_sql
    for item in compose:
        sql_statement = """UPDATE store SET"""
        sql_statement += " 工序库存=" + str(item.store_1)
        sql_statement += " where 物料名称='" + str(item.child)+"'"
        # print(sql_statement)
        await exec_sql(sql_statement)
        sql_statement = """UPDATE store SET"""
        sql_statement += " 资材库存=" + str(item.store_2)
        sql_statement += " where 物料名称='" + str(item.child)+"'"
        # print(sql_statement)
        await exec_sql(sql_statement)
    return

###############################################################################################


async def clear():
    global MPS_que_index
    global MPS_obj_que
    global MPS_output_que
    global ans
    await mutex_for_mps.acquire()
    try:
        MPS_que_index=0
        MPS_output_que=[]
        MPS_obj_que = []
        ans=[]
    finally:
        mutex_for_mps.release()


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


async def add_func_x(name):
    global func_obj_que
    global func_index
    if name != '':
        for it in func_obj_que:
            it.outp = [it.name, '=']
        func_obj_que.append(collect(name, func_index))
        func_que.append(name)
        func_index += 1


async def show_func():
    global func_ans_que
    func_ans_que=[]
    global func_index
    global func_obj_que
    from connectdb import select_from_db
    bom = await select_from_db("select * from bom")

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
                # print(y[3], num, x.outp)
                flag_x_exist = 0
        if flag_x_source == 0:
            x.outp = ["未找到资产流入来源"]
    for x in func_obj_que:
        s = ''.join(x.outp)
        func_ans_que.append(x.name+"  "+s)


async def func_clear():
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


async def get_supply_available():
    supply_available = []
    from connectdb import select_from_db
    sql_res = await select_from_db("""select DISTINCT inventory."父物料名称" from inventory""")
    for item in sql_res:
        if item[0] != "" and item[0] is not None:
            supply_available.append(item)
    return supply_available


@app.get("/")
async def root(request: Request,
               action: str = ""):  # 定义根路由处理函数，接受Request对象作为参数
    if action == "show":
        await show_result()
    if action == "clear":
        await clear()  # 调用clear函数
    supply_available = await get_supply_available()
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,
                                                     "que": MPS_output_que,
                                                     "supply_available":supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


@app.post("/")
async def root(request: Request,
                    pname: str = Form("default"),
                    num: str = Form("0"),
                    date: str = Form("2002-11-13")):  # 定义根路由下的POST请求处理函数，接受Request对象和表单数据作为参数
    # print(pname, num, date)  # 打印表单数据
    await add_mps(pname, int(num), date)  # 调用add函数处理表单数据
    supply_available = await get_supply_available()
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,
                                                     "que": MPS_output_que,
                                                     "supply_available":supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量



#########################################################################


@app.get("/store/")
async def root(request: Request):
    from connectdb import select_from_db
    store_list = await select_from_db("""select * from store""")
    return templates.TemplateResponse("store.html", {"request": request,
                                                    "store": store_list})


@app.post("/store/")
async def root(request: Request,
               pname: str = Form("default"),
               num1: str = Form("0"),
               num2: str = Form("0")):
    sql_statement = """update store set 工序库存={num1:d}, 资材库存={num2:d} 
    where 物料名称='{pname:s}'""".format(pname=pname,num1=int(num1),num2=int(num2))

    from connectdb import select_from_db, exec_sql
    await mutex_for_store.acquire()
    try:
        await exec_sql(sql_statement)
    finally:
        mutex_for_store.release()
    store_list = await select_from_db("""select * from store""")
    return templates.TemplateResponse("store.html", {"request": request,
                                                    "store": store_list})


#########################################################################################

async def get_x_available():
    from connectdb import select_from_db
    sql_x_res = await select_from_db("""SELECT bom."变量名" from bom 
    WHERE bom."变量名" IS NOT NULL and bom."变量名" != ''""")
    x_available = []
    for item in sql_x_res:
        x_available.append(item[0])
    return x_available


@app.get("/func/")
async def root(request: Request,
               action: str = ""):
    out = []
    if action == "show":
        await show_func()
        out = func_ans_que
    if action == "clear":
        await func_clear()
        out = func_que
    x_available = await get_x_available()
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": out,
                                                    "x_available": x_available})


@app.post("/func/")
async def root(request: Request,
            x=Form("")):
    await add_func_x(x)
    # print(func_que)
    x_available=await get_x_available()
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": func_que,
                                                    "x_available": x_available})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)  # 运行FastAPI应用，监听本地主机的8080端口