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


async def show_result():
    await mutex_for_store.acquire()
    await mutex_for_mps.acquire()
    try:
        global ans
        sql_state="""
                SELECT inventory."父物料名称", inventory."子物料名称", supply."调配方式", inventory."构成数", 
                supply."损耗率", store."工序库存",store."资材库存",supply."作业提前期",inventory."配料提前期",
                inventory."供应商提前期" 
                FROM inventory,supply,store 
                WHERE inventory."子物料名称"=supply."名称" AND inventory."子物料名称"=store."物料名称";
            """
        from connectdb import select_from_db
        sql_res = await select_from_db(sql_state)
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
            if need_num <= 0:
                return
            need_num = math.ceil(need_num/(1-item[4]))  # 损耗
            real_need_num = need_num
            if need_num <= item[5]+item[6]:  # 库存够
                if need_num <= item[5]:  # 工序够用
                    start_time = end_time - datetime.timedelta(days=item[7])
                    ans.append([item[1], 0, item[2], start_time, end_time])
                    real_need_num = 0
                    refresh_store(item, need_num, 0)
                else:  # 工序不够，但加上资材库存够用
                    start_time = end_time - datetime.timedelta(days=item[7] + item[8])
                    ans.append([item[1], need_num - item[5], item[2], start_time, end_time])
                    real_need_num = 0
                    refresh_store(item, item[5], need_num - item[5])
            else:  # 库存不够（工序和资材库存加起来都不够用）
                start_time = end_time - datetime.timedelta(days=item[7] + item[8] + item[9])
                ans.append([item[1], need_num - item[5] - item[6], item[2], start_time, end_time])
                real_need_num = need_num - item[5] - item[6]
                refresh_store(item, item[5], item[6])

            child_items = []
            for child in compose:
                if child[0] == item[1]:
                    child_items.append(child)

            if len(child_items) == 0:
                return
            else:
                for child in child_items:
                    main_dfs(child, real_need_num*child[3], ans, start_time)

        for mps in MPS_obj_que:
            for item in compose:
                if mps.pname == item[1]:
                    main_dfs(item, mps.require, ans, mps.deadline)

        await refresh_db(compose)
    finally:
        mutex_for_store.release()
        mutex_for_mps.release()


async def refresh_db(compose):
    from connectdb import exec_sql
    for item in compose:
        sql_statement = """UPDATE store SET"""
        sql_statement += " 工序库存=" + str(item[5])
        sql_statement += " where 物料名称='" + str(item[1])+"'"
        # print(sql_statement)
        await exec_sql(sql_statement)
        sql_statement = """UPDATE store SET"""
        sql_statement += " 资材库存=" + str(item[6])
        sql_statement += " where 物料名称='" + str(item[1])+"'"
        # print(sql_statement)
        await exec_sql(sql_statement)
    return

###############################################################################################


async def clear():
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
async def root(request: Request):  # 定义根路由处理函数，接受Request对象作为参数
    supply_available = await get_supply_available()
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,
                                                     "que": MPS_output_que,
                                                     "supply_available":supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


@app.post("/erp/")
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


@app.get("/show/")
async def root(request: Request):  # 定义/show/路由的GET请求处理函数，接受Request对象作为参数
    await show_result()
    supply_available = await get_supply_available()
    return templates.TemplateResponse("index.html", {"request": request, "ans": ans,
                                                     "que": MPS_output_que,
                                                     "supply_available":supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量

@app.get("/clear/")
async def root(request: Request):  # 定义/clear/路由的GET请求处理函数，接受Request对象作为参数
    await clear()  # 调用clear函数
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
async def root(request: Request):
    x_available = await get_x_available()
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": func_que,
                                                    "x_available":x_available})

@app.post("/func/")
async def root(request: Request,
            x=Form("")):
    await add_func_x(x)
    # print(func_que)
    x_available=await get_x_available()
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": func_que,
                                                    "x_available":x_available})

@app.get("/func_show/")
async def root(request: Request):
    await show_func()
    x_available = await get_x_available()
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": func_ans_que,
                                                    "x_available":x_available})

@app.get("/func_clear/")
async def root(request: Request):
    await func_clear()
    x_available = await get_x_available()
    return templates.TemplateResponse("func.html", {"request": request,
                                                    "func_output": func_que,
                                                    "x_available": x_available})



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)  # 运行FastAPI应用，监听本地主机的8080端口