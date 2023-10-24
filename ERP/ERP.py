from ERP.MPS import MpsList
from ERP.Tree import ComposeTree


class ERP:
    def __init__(self, mutex_for_store):
        self.ans = []
        self.MpsList = MpsList()
        self.ComposeTree = ComposeTree(self.MpsList, self.ans, mutex_for_store)

    async def clear(self):
        await self.MpsList.clear_mps()
        await self.ComposeTree.clear()
