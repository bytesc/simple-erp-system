# simple-erp-system

✨ **基于 Python, FastAPI, sqlite3 的简单 ERP 计算系统**：实现 MPS(Master Production Schedule) 的计算，按时间分段计划企业应生产的最终产品的数量和交货期；资产负债表公式查询。

[个人网站：www.bytesc.top](http://www.bytesc.top) 包含项目 📌 [在线演示](http://www.bytesc.top)  📌 

[个人博客：blog.bytesc.top](http://blog.bytesc.top)

🔔 如有项目相关问题，欢迎在本项目提出`issue`，我一般会在 24 小时内回复。

🚩 欢迎参考、复用代码，但请遵守`LICENSE`文件中的开源协议（参考翻译见本文档末尾）。对本仓库内的实质性内容（包括但不限于数据，图片，文档）保留著作权。

## 功能介绍

- 根据 MPS(Master Production Schedule) 按时间分段计划企业应生产的最终产品的数量和交货期
- 实现资产负债表公式查询
- 注释详细，易复现
- 极简的项目架构
- 极简的页面布局，轻量化的前端代码

## 基本原理

🚩 系统架构：

![](./readme_img/img0.png)

🚩 算法流程：

![](./readme_img/imga.png)

- 通过读取数据库中的物料的子父关系表，建立物料合成关系树
- 按照 MPS 队列和物料库存数量，DFS(Deep First Search)深度优先搜索计算生产和采购计划。

## 功能展示

添加 MPS 记录
![](./readme_img/img1.png)
产品名称从数据库中获取，用户可选择
![](./readme_img/img2.png)
点击计算，可一次性计算多条计划，按照时间优先级分配库存
![](./readme_img/img3.png)
资产负债公式变量同意从数据库中获取
![](./readme_img/img4.png)
可以一输出计算多个变量的公式
![](./readme_img/img5.png)
可手动修改库存信息（点击计算也会根据消耗自动更新库存）
![](./readme_img/img5.1.png)

## 数据库结构

`erpdata.db` 为 sqlite3 数据文件，`sql` 文件夹下包含数据库备份sql代码。

数据库结构
![](./readme_img/img6.png)
`supply`物料信息表
![](./readme_img/img7.png)
![](./readme_img/img8.png)
`inventory`物料构成清单
![](./readme_img/img9.png)
![](./readme_img/img10.png)
`store`库存表
![](./readme_img/img11.png)
![](./readme_img/img12.png)
`bom`资产负债信息表
![](./readme_img/img13.png)
![](./readme_img/img14.png)

## 项目运行

环境`python 3.9`

安装依赖
```bash
pip install -r requirements.txt
```
运行
```
python erpsys.py
```
浏览器访问 [http://127.0.0.1:8080](http://127.0.0.1:8080)即可进入系统

如果8080端口被占用，修改`erpsys.py`文件末尾的端口配置 (port) 即可。
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8081) 
```
注意，如果这里 `host="0.0.0.0"` 代表允许所有host访问，请依然浏览器输入 [http://127.0.0.1:8080](http://127.0.0.1:8080) 而不是 [http://0.0.0.0:8080](http://0.0.0.0:8080) 

## 项目结构

```txt
│  connectdb.py
│  erpdata.db
│  erpsys.py
│  LICENSE
│  README.md
│  requirements.txt
├─templates
│      func.html
│      index.html
├─readme_img
├─sql
       structure_data.sql
       structure_only.sql
```

- `erpsys.py` 是最主要的源代码文件，包含服务端代码和核心算法，也是项目的运行入口
- `connectdb.py` 包含数据库配置，连接，查询程序
- `erpdata.db` sqlite3 数据库文件
- `templates` 文件夹存放待渲染的 html 模板文件
- `sql` 文件夹存放创建数据库的 sql 代码

## 有待完善的部分

- 安全性：访问控制尚不完善。
- 健壮性：异常处理机制尚不完善。
- 多用户：目前多用户共享数据区，不能独立计算。

# 开源许可证

此翻译版本仅供参考，以 LICENSE 文件中的英文版本为准

MIT 开源许可证：

版权所有 (c) 2023 bytesc

特此授权，免费向任何获得本软件及相关文档文件（以下简称“软件”）副本的人提供使用、复制、修改、合并、出版、发行、再许可和/或销售软件的权利，但须遵守以下条件：

上述版权声明和本许可声明应包含在所有副本或实质性部分中。

本软件按“原样”提供，不作任何明示或暗示的保证，包括但不限于适销性、特定用途适用性和非侵权性。在任何情况下，作者或版权持有人均不对因使用本软件而产生的任何索赔、损害或其他责任负责，无论是在合同、侵权或其他方面。