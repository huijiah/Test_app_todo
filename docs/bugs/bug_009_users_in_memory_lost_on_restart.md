# Bug #009 — 用户数据存内存字典，服务重启后全部丢失

| 属性 | 值 |
|------|-----|
| **严重级别** | P2 - Minor |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` 第 8 行 |
| **影响范围** | `/register`、`/login` |

## 问题定位

```python
# routes.py:8
users = {"admin": "admin123"}
```

`users` 是模块级字典变量，存储在 Flask 进程内存中。每次容器重启 / 进程重启 / 多实例部署，`users` 都会重置为初始值。

任务数据（MySQL）是持久的，注册用户却是临时的——数据一致性不对称。

## 复现步骤

```bash
# 1. 注册一个用户
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# 2. 重启容器
docker compose restart app

# 3. 用刚才注册的账号登录
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

## 预期结果

登录成功。

## 实际结果

返回 `401`，用户已不存在。

## 修复建议

将用户表也存入 MySQL，添加 `users` 建表语句到 `init.sql`，`/register` 和 `/login` 走数据库读写。
