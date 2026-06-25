# Bug #010 — 密码明文存储

| 属性 | 值 |
|------|-----|
| **严重级别** | P2 - Minor（安全类） |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` 第 15 行 |
| **影响范围** | `/register` |

## 问题定位

```python
# routes.py:15
users[username] = password   # 直接存明文
```

无哈希、无盐，密码以明文存放于内存字典。即使这是演示项目，也不推荐——初学者容易以此为模板。

## 复现步骤

审查 `routes.py` 源码即可确认，无运行时复现步骤。

## 修复建议

引入 `werkzeug.security`（Flask 自带）：

```python
from werkzeug.security import generate_password_hash, check_password_hash

# 注册时
users[username] = generate_password_hash(password)

# 登录时
if not check_password_hash(users.get(username, ''), password):
    return jsonify(message="用户名或密码错误"), 401
```
