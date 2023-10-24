import copy
import datetime
import math

from connectdb import select_from_db, exec_sql


class ComposeItem:
    def __init__(self, father, child, way, comp_num,
                 loss_rate, store_1, store_2, adv_work, adv_make, adv_supply):
        self.father = father
        self.pname = child
        self.way = way  # 调配方式
        self.comp_num = comp_num
        self.loss_rate = loss_rate
        self.store_1 = store_1  # 工序库存
        self.store_2 = store_2  # 资材库存
        self.adv_work = adv_work  # 作业提前期
        self.adv_make = adv_make  # 配料提前期
        self.adv_supply = adv_supply  # 供应商提前期


class Node:
    def __init__(self, compose_item: ComposeItem):
        self.pname = compose_item.pname
        self.father = compose_item.father
        self.depth = -1  # 节点深度
        self.child_depth = -1  # 子树的深度

        self.children = []


class ComposeTree:
    def __init__(self, MpsList, ans, mutex_for_store):
        self.mutex_for_store = mutex_for_store
        self.MpsList = MpsList
        self.ans = ans
        self.compose = []

    def build_tree(self, root: Node, depth):
        root.depth = depth
        for item in self.compose:
            if item.father == root.pname:
                root.children.append(Node(item))
        if len(root.children) == 0:
            return
        for node in root.children:
            self.build_tree(node, depth + 1)

    def mark_child_depth(self, root: Node):  # 标记所有节点子树最大深度
        if len(root.children) == 0:
            root.child_depth = root.depth
            return
        for child in root.children:
            self.mark_child_depth(child)
        for child in root.children:
            root.child_depth = max(root.child_depth, child.child_depth)

    def refresh_store(self, item: Node, store_1, store_2):  # 刷新库存
        for i in self.compose:
            if i.pname == item.pname:
                i.store_1 -= store_1
                i.store_2 -= store_2

    async def refresh_db(self):
        for item in self.compose:
            sql_statement = """UPDATE store SET"""
            sql_statement += " 工序库存=" + str(item.store_1)
            sql_statement += " where 物料名称='" + str(item.pname) + "'"
            # print(sql_statement)
            await exec_sql(sql_statement)
            sql_statement = """UPDATE store SET"""
            sql_statement += " 资材库存=" + str(item.store_2)
            sql_statement += " where 物料名称='" + str(item.pname) + "'"
            # print(sql_statement)
            await exec_sql(sql_statement)
        return

    def main_dfs(self, node: Node, need_num, ans, end_time):
        item = None
        for i in self.compose:
            if i.pname == node.pname and i.father == node.father:
                item = i
        if need_num <= 0:
            return
        need_num = math.ceil(need_num / (1 - item.loss_rate))  # 损耗
        if need_num <= item.store_1 + item.store_2:  # 库存够
            if need_num <= item.store_1:  # 工序够用
                start_time = end_time - datetime.timedelta(days=item.adv_supply)
                ans.append([item.pname, 0, item.way, start_time, end_time])
                real_need_num = 0
                self.refresh_store(item, need_num, 0)
            else:  # 工序不够，但加上资材库存够用
                start_time = end_time - datetime.timedelta(days=item.adv_supply + item.adv_make)
                ans.append([item.pname, need_num - item.store_1, item.way, start_time, end_time])
                real_need_num = 0
                self.refresh_store(item, item.store_1, need_num - item.store_1)
        else:  # 库存不够（工序和资材库存加起来都不够用）
            start_time = end_time - datetime.timedelta(days=item.adv_supply + item.adv_make + item.adv_work)
            ans.append([item.pname, need_num - item.store_2 - item.store_1, item.way, start_time, end_time])
            real_need_num = need_num - item.store_1 - item.store_2
            self.refresh_store(item, item.store_1, item.store_2)

        if len(node.children) == 0:
            return
        else:
            node.children.sort(key=lambda x: -x.child_depth)  # 按子树深度倒序，先遍历深的
            for child in node.children:
                comp_num = 1
                for i in self.compose:
                    if i.pname == child.pname and i.father == child.father:
                        comp_num = i.comp_num
                self.main_dfs(child, real_need_num * comp_num, ans, start_time)

    async def show_result(self):
        await self.mutex_for_store.acquire()
        await self.MpsList.mutex_for_mps.acquire()
        try:
            self.compose.clear()
            self.ans.clear()  # 这里不能ans=[],这样会让ans指向另一个内存空间上的另一个新数组，而不是init传来的数组
            sql_state = """
                    SELECT inventory."父物料名称", inventory."子物料名称", supply."调配方式", inventory."构成数", 
                    supply."损耗率", store."工序库存",store."资材库存",supply."作业提前期",inventory."配料提前期",
                    inventory."供应商提前期" 
                    FROM inventory,supply,store 
                    WHERE inventory."子物料名称"=supply."名称" AND inventory."子物料名称"=store."物料名称";
                """
            sql_res = await select_from_db(sql_state)
            # print(sql_res)

            for i in sql_res:
                self.compose.append(ComposeItem(*i))

            for mps in self.MpsList.MPS_obj_que:  # 遍历 mps 队列计算结果
                for item in self.compose:
                    if item.pname == mps.pname:
                        root = Node(item)
                        self.build_tree(root, 0)
                        self.mark_child_depth(root)
                        self.main_dfs(root, mps.require, self.ans, mps.deadline)

            await self.refresh_db()
        finally:
            self.mutex_for_store.release()
            self.MpsList.mutex_for_mps.release()

    async def clear_tree(self):
        pass


