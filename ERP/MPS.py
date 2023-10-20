import asyncio
import datetime


class MpsObj:
    def __init__(self, pname, require, deadline, index):
        self.pname = pname
        self.require = require
        self.deadline = deadline
        self.index = index


class MpsList:
    def __init__(self):
        self.MPS_output_que = []
        self.MPS_obj_que = []
        self.MPS_que_index = 0
        self.mutex_for_mps = asyncio.Lock()

    async def add_mps(self, pname, require, deadline):
        await self.mutex_for_mps.acquire()
        try:
            if pname != '' and require != '' and deadline != '':
                deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d').date()
                self.MPS_obj_que.append(MpsObj(pname, require, deadline, self.MPS_que_index))
                self.MPS_output_que.append([pname, require, deadline,  self.MPS_que_index])
                self.MPS_que_index = self.MPS_que_index + 1  # 录入一次就+1

                self.MPS_obj_que.sort(key=lambda item: item.deadline)
        finally:
            self.mutex_for_mps.release()

    async def clear_mps(self):
        await self.mutex_for_mps.acquire()
        try:
            self.MPS_output_que = []
            self.MPS_obj_que = []
            self.MPS_que_index = 0
        finally:
            self.mutex_for_mps.release()
