# Bug #001 — `/login` 请求体缺少字段导致 KeyError → 500

| 属性 | 值 |
|------|-----|
| **严重级别** | P0 - Critical |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` 第 21 行 |
| **影响范围** | `/login` 接口 |

## 问题定位

```python
# routes.py:19-24
@task_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if users.get(data['username']) == data['password']:   # ← 直接取键，没校验
        token = create_access_token(identity=data['username'])
        return jsonify(access_token=token), 200
    return jsonify(message="Credenciales inválidas"), 401
```

未校验 `data` 是否为 `None`，也未用 `.get()` 安全取值，字段缺失直接抛 `KeyError`。

## 复现步骤

**前置条件：** Docker 服务已启动

```bash
# 用例 1：不传 username
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"password": "admin123"}'

# 用例 2：不传 password
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin"}'

# 用例 3：空 body
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 预期结果

返回 `400`，附带明确字段提示：
```json
{"message": "缺少必填字段: username"}
```

## 实际结果

返回 `500 Internal Server Error`，服务端日志：

```
KeyError: 'username'
  File "routes.py", line 21, in login
    if users.get(data['username']) == data['password']:
```

## 修复建议

```python
@task_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify(message="请求体不能为空"), 400
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify(message="缺少必填字段"), 400
    if users.get(username) != password:
        return jsonify(message="用户名或密码错误"), 401
    token = create_access_token(identity=username)
    return jsonify(access_token=token), 200
```
