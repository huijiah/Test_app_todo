# Bug #012 — `/tasks GET` 无分页，数据量大时一次性返回全部

| 属性 | 值 |
|------|-----|
| **严重级别** | P2 - Minor |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` 第 28-35 行 |
| **影响范围** | `GET /tasks` |

## 问题定位

```python
# routes.py:28-35
@task_routes.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")    # ← 全表查询，无 LIMIT/OFFSET
    rows = cursor.fetchall()                 # ← 一次性加载所有行到内存
    tasks = [{'id': row[0], 'description': row[1]} for row in rows]
    conn.close()
    return jsonify(tasks)
```

当任务数量增长到万级，单次请求返回全部数据会打满内存和带宽。

## 复现步骤

循环创建大量任务后请求 `/tasks`，观察响应体大小和响应时间。

## 修复建议

增加 `page` 和 `per_page` 查询参数：

```python
@task_routes.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM tasks LIMIT %s OFFSET %s", (per_page, offset))
        rows = cursor.fetchall()
    conn.close()
    return jsonify(tasks), 200
```
