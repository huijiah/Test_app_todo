import requests
import pytest
from config.settings import BASE_URL

class TestLoginMissingFields:
    """Bug #1: /login 缺少请求体字段校验导致 KeyError 500"""

    @pytest.mark.xfail(reason="已知缺陷：缺少字段校验，应返回400却返回500")
    def test_login_without_username(self):
        """缺少 username 字段"""
        res = requests.post(f"{BASE_URL}/login", json={"password": "123456"})
        assert res.status_code == 400  # 期望400，当前实际500

    @pytest.mark.xfail(reason="已知缺陷：缺少字段校验，应返回400却返回500")
    def test_login_without_password(self):
        """缺少 password 字段"""
        res = requests.post(f"{BASE_URL}/login", json={"username": "admin"})
        assert res.status_code == 400

    @pytest.mark.xfail(reason="已知缺陷：缺少字段校验，应返回400却返回500")
    def test_login_with_empty_body(self):
        """空对象"""
        res = requests.post(f"{BASE_URL}/login", json={})
        assert res.status_code == 400

    @pytest.mark.xfail(reason="已知缺陷：Content-Type非法时应返回400")
    def test_login_wrong_content_type(self):
        """Content-Type 非 JSON"""
        res = requests.post(
            f"{BASE_URL}/login",
            data="hello",
            headers={"Content-Type": "text/plain"}
        )
        assert res.status_code == 400