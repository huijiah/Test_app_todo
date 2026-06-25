# Bug #006 — 数据库 cursor 对象未关闭，连接泄漏

| 属性 | 值 |
|------|-----|
| **严重级别** | P1 - Major |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` 第 30/43 行 |
| **影响范围** | `GET /tasks`、`POST /tasks` |

## 问题定位

```python
# routes.py GET /tasks
cursor = conn.cursor()
cursor.execute("SELECT * FROM tasks")
rows = cursor.fetchall()
# cursor.close() 缺失 ← 泄漏
conn.close()

# routes.py POST /tasks
cursor = conn.cursor()
cursor.execute("INSERT INTO tasks (description) VALUES (%s)", (data['description'],))
conn.commit()
# cursor.close() 缺失 ← 泄漏
conn.close()
```

每条请求创建 cursor 对象后从未调用 `cursor.close()`，cursor 占用内存不会立即释放。低并发时不可感知，高并发时 MySQL 连接数被占满、服务不可用。

## 复现方法

用 Apache Bench 或 wrk 对 `/tasks` 持续并发请求，观察 MySQL 连接数：

```bash
# 终端 1：监控 MySQL 连接数
watch -n 1 'docker exec <db_container> mysql -u root -prootpassword -e "SHOW PROCESSLIST"'

# 终端 2：并发请求
ab -n 5000 -c 100 http://localhost:5000/tasks
```

## 预期结果

连接数稳定，请求结束后释放。

## 实际结果

连接数持续上升，峰值远超预期。

## 修复建议

常规写法：`with` 语句由上下文管理器自动关闭 cursor。

```python
with conn.cursor() as cursor:
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
```
