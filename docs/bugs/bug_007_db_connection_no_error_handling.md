# Bug #007 — 数据库连接无异常处理，MySQL 不可用时返回 HTML 500

| 属性 | 值 |
|------|-----|
| **严重级别** | P1 - Major |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/models.py:5-10` |
| **影响范围** | `GET /tasks`、`POST /tasks` |

## 问题定位

```python
# models.py
def get_db_connection():
    return MySQLdb.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        passwd=os.environ.get('DB_PASSWORD'),
        db=os.environ.get('DB_NAME')
    )
```

连接失败时 `MySQLdb.connect()` 直接抛出异常，Flask 没有自定义错误处理器，返回 HTML 格式的 500 堆栈页面。API 应始终返回 JSON。

## 复现步骤

```bash
# 1. 只停掉 MySQL 容器
docker stop <db_container_name>

# 2. 请求需要数据库的接口
curl -X GET http://localhost:5000/tasks \
  -H "Authorization: Bearer <token>"
```

## 预期结果

返回 `503` JSON：
```json
{"message": "数据库服务不可用，请稍后重试"}
```

## 实际结果

返回 `500`，响应体为 HTML：
```html
<!DOCTYPE HTML PUBLIC ...>
<title>500 Internal Server Error</title>
<p>MySQLdb.OperationalError: (2003, "Can't connect to MySQL server ...")</p>
```

## 修复建议

1. `get_db_connection()` 内包 try-except
2. Flask 全局注册错误处理器，将所有异常统一转 JSON：

```python
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify(message="服务器内部错误"), 500
```
