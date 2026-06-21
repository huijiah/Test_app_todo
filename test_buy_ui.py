import pytest
import time
from selenium.webdriver.common.by import By


def test_saucedemo_checkout_process(driver):
    """测试用例2：登录后购买一件商品并结账"""

    # 1. 执行登录动作
    driver.get("https://www.saucedemo.com/")
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()

    # 2. 点击加入购物车
    driver.find_element(By.CSS_SELECTOR, "#add-to-cart-sauce-labs-backpack").click()

    # 3. 点击购物车
    driver.find_element(By.CSS_SELECTOR, ".shopping_cart_link").click()

    # 4. 点击结账
    driver.find_element(By.ID, "checkout").click()

    # 5. 填写表单
    driver.find_element(By.ID, "first-name").send_keys("Test")
    driver.find_element(By.ID, "last-name").send_keys("User")
    driver.find_element(By.ID, "postal-code").send_keys("123456")
    driver.find_element(By.ID, "continue").click()

    # 6. 断言概览页
    assert "Checkout: Overview" in driver.page_source

    # 7. 点击完成
    driver.find_element(By.ID, "finish").click()

    # 8. 最终断言成功
    assert "Thank you for your order" in driver.page_source

    print("✅ UI 全流程通过！成功买了一件商品并结账。")
    time.sleep(3)