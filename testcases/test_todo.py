import requests
import pytest
from config.settings import BASE_URL, USERNAME, PASSWORD, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
import pymysql
import sys
import os

@pytest.mark.parametrize("task_desc", [
    "普通中文测试任务",
    "Special Characters !@#$%",
    "1234567890"
])
def test_parametrize_create_tasks(auth_token, task_desc):
    """参数化测试：用 3 种不同的描述来创建任务"""

    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"description": task_desc}

    response = requests.post(f"{BASE_URL}/tasks", json=payload, headers=headers)

    # 断言接口返回 201
    assert response.status_code == 201
    print(f"✅ 成功创建任务，描述为: {task_desc}")

@pytest.fixture(scope="module")
def auth_token():
    """这是一个前置操作：先注册，再登录，最后把获取到的 Token 返回给测试用例使用"""

    # 1. 注册用户
    register_data = {"username": USERNAME, "password": PASSWORD}
    requests.post(f"{BASE_URL}/register", json=register_data)

    # 2. 登录获取 Token
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(f"{BASE_URL}/login", json=login_data)

    # 断言登录必须成功
    assert response.status_code == 200, f"登录失败: {response.text}"

    # 提取并返回 Token
    token = response.json().get("access_token")
    return token


def test_create_task_and_db_verify(auth_token):
    """进阶测试：调用 API 创建任务，数据库验证，并自动清理数据"""

    headers = {"Authorization": f"Bearer {auth_token}"}
    task_desc = "MySQL验证测试数据"
    payload = {"description": task_desc}

    # 1. 发送 API 请求创建任务
    response = requests.post(f"{BASE_URL}/tasks", json=payload, headers=headers)
    assert response.status_code == 201

    # 2. 手动连接 MySQL 数据库去查数据
    conn = pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME
    )

    task_id = None  # 用于记录查到的 ID

    try:
        with conn.cursor() as cursor:
            # 查询刚刚创建的数据
            sql = "SELECT id, description FROM tasks WHERE description = %s"
            cursor.execute(sql, (task_desc,))
            result = cursor.fetchone()

            # 断言数据库存在该记录
            assert result is not None, f"数据库找不到描述为 '{task_desc}' 的记录"
            task_id = result[0]  # 把查到的 ID 记下来，为下一步删除做准备
            print(f"✅ 数据库验证成功！查到记录 -> ID: {task_id}")

    finally:
        # 3. 垃圾数据删除
        if task_id:
            with conn.cursor() as cursor:
                delete_sql = "DELETE FROM tasks WHERE id = %s"
                cursor.execute(delete_sql, (task_id,))
                conn.commit()  # 提交删除操作
                print(f"🧹 环境清理完成，已删除 ID 为 {task_id} 的测试数据")

        # 4. 关闭数据库连接
        conn.close()

def test_get_tasks(auth_token):
    """测试用例 2：获取任务列表"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = requests.get(f"{BASE_URL}/tasks", headers=headers)

    # 断言：断言状态码必须是 200
    assert response.status_code == 200

    # 打印一下获取到的结果看看（原本是一个 JSON 列表）
    tasks = response.json()
    print(f"✅ 获取任务列表成功，当前共有 {len(tasks)} 条任务。")


def test_unauthorized_access():
    """测试不携带 Token 时，是否会被接口拒绝"""
    # 故意不带 headers
    response = requests.get(f"{BASE_URL}/tasks")

    # 断言：如果不带 token，应当返回 401 Unauthorized 或者 422
    # 您可以先打印一下 response.status_code 看看您的项目会返回什么
    assert response.status_code == 401

    # 通常这里您会写：assert response.status_code == 401
