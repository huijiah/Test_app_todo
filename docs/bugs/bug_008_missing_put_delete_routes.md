# Bug #008 — 缺少任务更新和删除接口

| 属性 | 值 |
|------|-----|
| **严重级别** | P1 - Major |
| **发现版本** | 源码 commit `main` 分支 |
| **发现日期** | 2025-06-20 |
| **定位文件** | `app/routes.py` |
| **影响范围** | API 功能完整性 |

## 问题定位

`routes.py` 只注册了：

```
POST   /register
POST   /login
GET    /tasks
POST   /tasks
```

遗漏了：
- `PUT /tasks/<id>` — 更新任务
- `DELETE /tasks/<id>` — 删除任务

用户创建任务后无法修改或删除，API 不符合 RESTful CRUD 规范。

## 复现步骤

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 尝试删除任务
curl -X DELETE http://localhost:5000/tasks/1 \
  -H "Authorization: Bearer $TOKEN"

# 尝试更新任务
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"description": "更新后的内容"}'
```

## 预期结果

`DELETE` 返回 `200`，`PUT` 返回 `200` 并返回更新后的数据。

## 实际结果

返回 `404 Not Found`。

## 修复建议

增加两个路由：

```python
@task_routes.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    data = request.get_json()
    # 校验 + 更新逻辑

@task_routes.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    # 删除逻辑
```
