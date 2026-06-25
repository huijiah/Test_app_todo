# To-Do-App 接口自动化测试

对 [To-Do-App](https://github.com/Zero9BSC/To-Do-App)（Flask + MySQL + JWT）的接口自动化测试项目，覆盖功能测试、异常测试、数据库一致性验证，并集成 CI 流水线与测试报告。

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| 测试框架 | Pytest + Requests + PyMySQL |
| 报告 | Allure |
| CI/CD | GitHub Actions |
| 环境 | Docker Compose |

## 项目结构

```
Test_app_todo/
├── .github/workflows/test.yml   # CI 流水线（自动拉取源码、启动服务、运行测试）
├── config/
│   └── settings.py              # API 地址、数据库连接信息、测试账号
├── testcases/
│   ├── conftest.py              # 夹具：Token 获取、数据库连接、数据清理
│   └── test_todo.py             # 测试用例（注册/登录/任务 CRUD）
├── docs/
│   └── bugs/                    # 发现的缺陷记录
├── requirements.txt             # Python 依赖
└── report.html                  # Allure 测试报告
```

## 快速开始

### 1. 启动被测服务

```bash
git clone https://github.com/Zero9BSC/To-Do-App.git
cd To-Do-App
docker compose up -d
```

### 2. 安装测试依赖

```bash
pip install -r requirements.txt
```

### 3. 运行测试

```bash
# 全部用例
pytest testcases/ -v

# 指定文件
pytest testcases/test_todo.py -v

# 生成 Allure 报告
pytest testcases/ -v --alluredir=allure-results
allure generate allure-results -o allure-report --clean
allure open allure-report
```

## 测试范围

| 模块 | 用例 | 覆盖场景 |
|------|------|---------|
| 注册/登录 | 4 | 正常注册登录、错误密码、不存在用户、缺少字段 |
| 创建任务 | 4 | 参数化创建（中文/英文/数字）、数据库验证+清理、缺少字段、空值 |
| 获取任务 | 3 | 正常获取、无 Token、伪造 Token |

## Fixture 设计

| Fixture | Scope | 说明 |
|---------|-------|------|
| `api_session` | session | 复用 requests.Session，减少 TCP 握手开销 |
| `auth_token` | module | 自动完成注册→登录→返回 Token，整个模块执行一次 |
| `auth_headers` | function | 基于 auth_token 拼装 Authorization 头 |
| `db_connection` | function | 独立 MySQL 连接，teardown 自动关闭 |
| `clean_test_data` | function | 注册清理 SQL，teardown 时批量执行 |

## CI 流程

push 到 main/master 分支时自动触发：

1. 拉取测试项目代码
2. 拉取原项目源码（Zero9BSC/To-Do-App）
3. 安装 Python + 测试依赖 + Allure CLI
4. 启动被测服务（Docker Compose）
5. 执行 pytest 并输出 Allure 结果
6. 生成 Allure 报告并上传为 Artifact

## 发现的缺陷

详见 `docs/bugs/` 目录，典型问题包括：

- [ ] `/login` 缺少请求体字段时 KeyError → 500
- [ ] `/tasks POST` 缺少 description 字段时 KeyError → 500
- [ ] `description` 无长度校验，超 VARCHAR(255) 静默截断
- [ ] 数据库连接无异常处理，DB 不可用时返回 HTML 500
- [ ] cursor 对象未关闭，存在资源泄漏
- [ ] 用户数据存内存，服务重启后丢失
