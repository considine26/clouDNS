# 🌌 ClouDNS DNS  API 管理

欢迎使用 **ClouDNS DNS 智能 API 终端管理终端**

---

## 📂 项目目录结构

```text
ClouDNS/
├── core/
│   ├── __init__.py
│   ├── api_client.py       # API 客户端核心（负责鉴权与 HTTP 通讯）
│   ├── config_manager.py   # 配置文件管理器（负责加载与读写 users.json）
│   ├── dns.py              # DNS CRUD 操作逻辑层
│   └── cli.py              # Rich 终端美化与键盘方向键交互核心
├── users.json              # API 账号与域名绑定的本地配置文件
├── README.md               # 项目使用说明文档（本文件）
└── main.py                 # 项目统一主入口脚本
```

---

## 🚀 快速开始与环境安装

项目推荐使用先进的 Python 依赖及环境管理工具 **`uv`**，以便快速、零污染地部署运行。

### 1. 安装 `uv` (如已安装可跳过)

```powershell
pip install uv
```

### 2. 一键运行终端

在项目根目录下，直接执行：

```powershell
uv run python main.py
```

`uv` 会自动在后台隔离沙箱中下载 Python 环境与依赖库（如 `rich`, `requests` 等），并直接秒开进入程序！

---

## ⚙️ 配置文件指南 (`users.json`)

系统支持**多账户（Profiles）**以及**多域名（Domain Name List）**的动态联动配置。编辑根目录下的 `users.json` 文件即可管理您的账户凭证：

```json
{
    "version": "2.0",
    "api_base_url": "https://api.cloudns.net/",
    "profiles": {
        "user01": {
            "auth_id": "59555",
            "auth_password": "你的32位API账户密码Hash",
            "domain_name": [
                "xxx.cloudns.be"
            ],
            "last_used_at": ""
        }, 
        "user02": {
            "auth_id": "59666",
            "auth_password": "你的32位API账户密码Hash",
            "domain_name": [
                "xxx.ip-ddns.com",
                "yyy.cloudns.be"
            ],
            "last_used_at": ""
        }
    }
}
```

### 💡 关键字段说明

* `auth_id`：您的 ClouDNS API 用户 ID（通常为纯数字）。
* `auth_password`：您在 API 用户中设定的密码（32位 MD5 Hash）。
* `domain_name`：**域名列表（重要）**。您可以为其绑定一个或多个主域名。

---

## 🎮 终端交互与高级特性

进入主控制台后，您将获得以下选项：

* **📋 列出 DNS 解析记录**：
  以极具视觉冲击力的 Rich 炫彩表格渲染该域名下的所有记录，包含 ID、主机名、记录类型、目标值及 TTL。
* **➕ 添加 DNS 解析记录**：
  支持 `A`、`AAAA`、`CNAME`、`TXT`、`MX` 等主流类型，内置向导式智能交互。
* **✏️ 修改 DNS 解析记录**：
  自动列出已有记录，输入 `Record ID` 即可修改对应字段（支持回车保留默认值）。
* **❌ 删除 DNS 解析记录**：
  支持删除前的安全双重校验 (`y/n`)，防止误删。

---

## ⚠️ 常见问题排查 (Troubleshooting)

### Q1：提示 `[✘] 获取失败: You don't have access to the HTTP API. Check your plan.`

* **原因**：这是 ClouDNS 官方的付费套餐封禁限制。ClouDNS 的全套管理 API（用于增删改查记录）只面向 **Premium / Reseller 付费用户** 开放。
* **解决方案**：建议在 ClouDNS 后台升级到最基础的 Premium 套餐（价格极度低廉，通常每月 < $1）；或者您也可以改用 ClouDNS 面向免费用户开放的免费 **Dynamic DNS (DDNS) 专用 URL 接口** 进行单条 A 记录的自动化 IP 更新。

### Q2：使用方向键选择菜单时没有反应或闪烁？

* **原因**：由于系统使用了 Windows 原生的 `msvcrt` 缓存库读取键盘扫描码，请确保您是在 **本地终端**（如 PowerShell、cmd.exe 或 Windows Terminal）中运行，而非某些 IDE 的内置非交互式仿真输出窗口中。

