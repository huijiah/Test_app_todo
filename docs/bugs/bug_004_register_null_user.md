# Bug #004 — `/register` 不校验空值，可注册 None 用户

| 属性 | 值 |
|------|-----|
| **严重级别** | P0 - Critical |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` 第 13-16 行 |
| **影响范围** | `/register` 接口 |

## 问题定位

```python
# routes.py:11-16
@task_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')      # 可能为 None
    password = data.get('password')      # 可能为 None
    users[username] = password           # users[None] = None ← 污染数据
    return jsonify(message="Usuario registrado"), 201
```

`.get()` 取不到时返回 `None`，没有任何 null 检查，直接将 `None: None` 写入用户字典。

## 复现步骤

```bash
# 用例 1：空 body
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{}'

# 用例 2：显式 null
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": null, "password": null}'

# 用例 3：只传 username
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test"}'
```

## 预期结果

返回 `400`，拒绝空值注册。

## 实际结果

返回 `201`，`users` 字典被写入 `None: None`。后果：后续 `/login` 传 `{"username": null, "password": null}` 可能绕过鉴权。

## 修复建议

```python
@task_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify(message="请求体不能为空"), 400
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify(message="用户名和密码不能为空"), 400
    if username in users:
        return jsonify(message="用户名已存在"), 409
    users[username] = password
    return jsonify(message="Usuario registrado"), 201
```
