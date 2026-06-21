import time
from selenium.webdriver.common.by import By


def test_saucedemo_login_success(driver):
    """测试用例：使用正确的账号密码登录成功"""

    # 1. 打开网页
    driver.get("https://www.saucedemo.com/")

    # 2. 输入账号和密码
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")

    # 3. 点击登录
    driver.find_element(By.ID, "login-button").click()

    # 4. 断言成功
    assert "Products" in driver.page_source, "登录失败，页面没有出现 Products 标题！"

    print("✅ UI 登录测试通过！")
    time.sleep(2)