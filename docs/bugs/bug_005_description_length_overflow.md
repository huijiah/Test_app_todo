# Bug #005 — `description` 字段无长度校验，超 VARCHAR(255) 静默截断

| 属性 | 值 |
|------|-----|
| **严重级别** | P1 - Major |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py:43` / `init.sql:7` |
| **影响范围** | `POST /tasks` 接口 |

## 问题定位

```python
# routes.py —— 无任何长度检查
cursor.execute("INSERT INTO tasks (description) VALUES (%s)", (data['description'],))
```

```sql
-- init.sql —— 字段限制 255 字符
description VARCHAR(255)
```

MySQL 非严格模式下，超长内容会被静默截断，用户数据丢失且无任何提示。

## 复现步骤

```bash
# 提交 500 字符的 description
TOKEN=$(curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

LONG_DESC=$(python3 -c "print('A' * 500)")

curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"description\": \"$LONG_DESC\"}"
```

## 预期结果

返回 `400`，提示超长：
```json
{"message": "description 超过最大长度 255"}
```

## 实际结果

返回 `201`，但数据库只存了前 255 个字符，后续内容丢失。

## 修复建议

在 `routes.py` 的 `create_task()` 中插入长度校验：
```python
if len(data['description']) > 255:
    return jsonify(message="description 超过最大长度 255"), 400
```
