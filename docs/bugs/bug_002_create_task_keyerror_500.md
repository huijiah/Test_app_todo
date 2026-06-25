# Bug #002 — `/tasks POST` 缺少 description 字段导致 KeyError → 500

| 属性 | 值 |
|------|-----|
| **严重级别** | P0 - Critical |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` 第 43 行 |
| **影响范围** | `POST /tasks` 接口 |

## 问题定位

```python
# routes.py:39-46
@task_routes.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (description) VALUES (%s)", (data['description'],))  # ← 硬取键
    conn.commit()
    conn.close()
    return jsonify(message="Tarea creada"), 201
```

未校验 `data` 和 `description` 字段是否存在，缺少时直接 `KeyError`。

## 复现步骤

```bash
# 1. 先获取一个合法 Token
TOKEN=$(curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 2. 不带 description 创建任务
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'

# 3. 空 body
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d ''
```

## 预期结果

返回 `400`：
```json
{"message": "缺少必填字段: description"}
```

## 实际结果

返回 `500 Internal Server Error`，服务端日志：
```
KeyError: 'description'
```

## 修复建议

```python
@task_routes.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify(message="缺少必填字段: description"), 400
    if not data['description'].strip():
        return jsonify(message="description 不能为空"), 400
    if len(data['description']) > 255:
        return jsonify(message="description 超过最大长度 255"), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (description) VALUES (%s)", (data['description'],))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(message="Tarea creada"), 201
```
