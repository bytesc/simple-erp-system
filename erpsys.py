import asyncio

##############################################################################################

from fastapi import FastAPI, Form  # 导入FastAPI和Form
from starlette.requests import Request  # 导入Request类
from starlette.templating import Jinja2Templates  # 导入Jinja2Templates类

app = FastAPI()  # 创建FastAPI应用实例
templates = Jinja2Templates(directory="templates")  # 创建Jinja2Templates实例，并指定模板目录为"templates"

##############################################################################################

from connectdb import select_from_db, exec_sql
from connectdb import get_store_available, get_supply_available
from connectdb import mutex_for_store  # 只允许一个修改库存

from ERP.ERP import ERP
ERPobj = ERP(mutex_for_store)

##############################################################################################


@app.get("/")
async def root(request: Request,
               action: str = ""):  # 定义根路由处理函数，接受Request对象作为参数
    if action == "show":
        await ERPobj.ComposeTree.show_result()
    if action == "clear":
        await ERPobj.clear()  # 调用clear函数
    supply_available = await get_supply_available()
    return templates.TemplateResponse("index.html", {"request": request, "ans": ERPobj.ans,
                                                     "que": ERPobj.MpsList.MPS_output_que,
                                                     "supply_available": supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


@app.post("/")
async def root(request: Request,
                    pname: str = Form("default"),
                    num: str = Form("0"),
                    date: str = Form("2002-11-13")):  # 定义根路由下的POST请求处理函数，接受Request对象和表单数据作为参数
    # print(pname, num, date)  # 打印表单数据
    await ERPobj.MpsList.add_mps(pname, int(num), date)  # 调用add函数处理表单数据
    supply_available = await get_supply_available()
    return templates.TemplateResponse("index.html", {"request": request, "ans": ERPobj.ans,
                                                     "que": ERPobj.MpsList.MPS_output_que,
                                                     "supply_available": supply_available})  # 返回使用模板"index.html"渲染的响应，传递request、ans和que作为模板变量


@app.get("/store/")
async def root(request: Request):
    store_list = await get_store_available()
    return templates.TemplateResponse("store.html", {"request": request,
                                                    "store": store_list})


@app.post("/store/")
async def root(request: Request,
               pname: str = Form("default"),
               num1: str = Form("0"),
               num2: str = Form("0")):
    sql_statement = """update store set 工序库存={num1:d}, 资材库存={num2:d} 
    where 物料名称='{pname:s}'""".format(pname=pname, num1=int(num1), num2=int(num2))

    await mutex_for_store.acquire()
    try:
        await exec_sql(sql_statement)
    finally:
        mutex_for_store.release()
    store_list = await get_store_available()
    return templates.TemplateResponse("store.html", {"request": request,
                                                    "store": store_list})


#########################################################################################
#########################################################################################
#########################################################################################


func_index = 0
func_obj_que = []
func_que = []
func_ans_que = []


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


#########################################################################################
#########################################################################################
#########################################################################################


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)  # 运行FastAPI应用，监听本地主机的8080端口
