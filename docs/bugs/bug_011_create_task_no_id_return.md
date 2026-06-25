# Bug #011 — `/tasks POST` 创建成功不返回 task ID

| 属性 | 值 |
|------|-----|
| **严重级别** | P2 - Minor |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` 第 46 行 |
| **影响范围** | `POST /tasks` |

## 问题定位

```python
# routes.py:43-46
cursor.execute("INSERT INTO tasks (description) VALUES (%s)", (data['description'],))
conn.commit()
conn.close()
return jsonify(message="Tarea creada"), 201   # ← 不返回 task id
```

调用方创建任务后无法得知新任务的 ID，后续若需更新或删除该任务（Bug #008 也提到缺路由），无法定位。

## 复现步骤

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"description": "测试任务"}'
```

## 预期结果

```json
{"message": "Tarea creada", "task_id": 42}
```

## 实际结果

```json
{"message": "Tarea creada"}
```

## 修复建议

```python
cursor.execute("INSERT INTO tasks (description) VALUES (%s)", (data['description'],))
conn.commit()
task_id = cursor.lastrowid
conn.close()
return jsonify(message="Tarea creada", task_id=task_id), 201
```
