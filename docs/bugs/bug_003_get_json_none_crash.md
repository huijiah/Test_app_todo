# Bug #003 — 所有接口未处理 `get_json()` 返回 None

| 属性 | 值 |
|------|-----|
| **严重级别** | P0 - Critical |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` 第 12/20/40 行 |
| **影响范围** | `/register`、`/login`、`POST /tasks` |

## 问题定位

`request.get_json()` 在请求 `Content-Type` 非 `application/json` 或 body 为空时返回 `None`，后续 `.get()` 调用抛出 `AttributeError`：

```python
# routes.py 三个接口都是这样写：
data = request.get_json()
username = data.get('username')   # data 为 None → AttributeError
```

## 复现步骤

```bash
# 以 /login 为例，故意发非 JSON 请求
curl -X POST http://localhost:5000/login \
  -H "Content-Type: text/plain" \
  -d 'not json'

# 或者完全不传 body
curl -X POST http://localhost:5000/login
```

## 预期结果

返回 `400`：
```json
{"message": "请求体必须为 JSON 格式"}
```

## 实际结果

返回 `500`，服务端日志：
```
AttributeError: 'NoneType' object has no attribute 'get'
```

## 影响评估

此问题影响 `/register`、`/login`、`POST /tasks` 共计 3 个接口。只要请求方误用了非 JSON 的 Content-Type，服务必然崩溃。

## 修复建议

在函数入口加判断：

```python
data = request.get_json()
if data is None:
    return jsonify(message="请求体必须为 JSON 格式"), 400
```

或统一用 Flask `@app.errorhandler` 注册全局异常处理，将所有未捕获异常转为 JSON 格式返回。
