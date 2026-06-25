import pytest
import requests
import pymysql
from config.settings import BASE_URL, USERNAME, PASSWORD, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


@pytest.fixture(scope="session")
def api_session():
    """复用 TCP 连接，避免每次请求都重新握手"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="module")
def auth_token(api_session):
    """
    模块级前置：注册 + 登录，返回 Token。
    scope=module 保证整个测试文件只执行一次。
    """
    api_session.post(f"{BASE_URL}/register", json={"username": USERNAME, "password": PASSWORD})
    resp = api_session.post(f"{BASE_URL}/login", json={"username": USERNAME, "password": PASSWORD})
    assert resp.status_code == 200, f"登录失败: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """每次用例调用时自动带上 Token，省去重复拼 headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def db_connection():
    """
    数据库连接 fixture。
    每个用例拿到独立连接，teardown 时自动关闭。
    """
    conn = pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME,
        charset="utf8mb4"
    )
    yield conn
    conn.close()


@pytest.fixture
def clean_test_data(db_connection):
    """
    提供数据清理能力。
    用例 yield 前执行测试逻辑，yield 后自动删数据。
    用法：
        def test_xxx(clean_test_data):
            clean_test_data("DELETE FROM tasks WHERE description = 'xxx'")
            # 测试结束后自动执行传入的 SQL
    """
    cleanup_sqls = []

    def schedule_cleanup(sql: str):
        cleanup_sqls.append(sql)

    yield schedule_cleanup

    with db_connection.cursor() as cursor:
        for sql in cleanup_sqls:
            cursor.execute(sql)
        db_connection.commit()
