# 🌌 ClouDNS DNS  API 管理

欢迎使用 **ClouDNS DNS 智能 API 终端管理终端**

---

## 📂 项目目录结构

项目采用了高内聚、低耦合的**模块化架构**拆分设计，根目录结构极其清爽：

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
打开 PowerShell 运行：
```powershell
pip install uv
```

### 2. 一键运行终端
在项目根目录 `d:\myproject\AIscript\ClouDNS` 下，直接执行：
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

### 💡 关键字段说明：
* `auth_id`：您的 ClouDNS API 用户 ID（通常为纯数字）。
* `auth_password`：您在 API 用户中设定的密码（32位 MD5 Hash）。
* `domain_name`：**域名列表（重要）**。您可以为其绑定一个或多个主域名。

---

## 🎮 终端交互与高级特性

运行程序后，您将体验到**专为 Windows 终端打磨的丝滑交互**：

### ⌨️ 1. 原生键盘高亮选择
* 使用键盘的 **`↑` / `↓` 方向键** 可以在菜单项之间上下滚动高亮。
* 选中所需功能或账号后，按 **`Enter` 回车键** 确认。
* 按 **`Esc` 键** 可安全返回上级或退出当前交互。

### 🧠 2. 独创的智能分流（Hybrid）登录过场
为了兼顾极致的“高效率”与清晰的“信息掌控”，系统设计了两种流线型过场：
* **单域名账户（闪电过场）**：
  若您选中的 API 账号在 `domain_name` 列表中仅绑定了 **1** 个域名，系统在您敲击回车选中账号的一瞬间，会**直接、静默、秒级**切入主控台，实现 0 延迟登录。
* **多域名账户（清晰提示）**：
  若账号绑定了**多个**域名，系统会首先清屏并展现绿色的 `✔ 账号激活成功！` 卡片以标明当前登录的主体。随后弹窗让您选择要操作的主域名，选定后停留 `0.8秒` 反馈确认，确保信息不出现断层。

### 📋 3. 六大核心控制功能
进入主控制台后，您将获得以下选项：
* **📋 列出 DNS 解析记录**：以极具视觉冲击力的 Rich 炫彩表格渲染该域名下的所有记录，包含 ID、主机名、记录类型、目标值及 TTL。
* **➕ 添加 DNS 解析记录**：支持 `A`、`AAAA`、`CNAME`、`TXT`、`MX` 等主流类型，内置向导式智能交互。
* **✏️ 修改 DNS 解析记录**：自动列出已有记录，输入 `Record ID` 即可修改对应字段（支持回车保留默认值）。
* **❌ 删除 DNS 解析记录**：支持删除前的安全双重校验 (`y/n`)，防止误删。
* **🔄 切换 API 账号**：**【特色功能】** 允许在不重启程序的情况下，直接一键热切换到其他 API 账户并联动新域名。
* **🚪 退出程序**：安全关闭终端，释放资源。

### 🧼 4. 极致清屏设计
每一个操作步骤（如“查看记录”或“添加记录”）执行时都会进行专门的**单帧清屏**。完成任务后，仅当您按下 `Enter` 时才会再次清屏并重建置顶的主控制台信息看板，使您的终端屏幕永远清爽、干净。

---

## ⚠️ 常见问题排查 (Troubleshooting)

### Q1：提示 `[✘] 获取失败: You don't have access to the HTTP API. Check your plan.`
* **原因**：这是 ClouDNS 官方的付费套餐封禁限制。ClouDNS 的全套管理 API（用于增删改查记录）只面向 **Premium / Reseller 付费用户** 开放。
* **解决方案**：建议在 ClouDNS 后台升级到最基础的 Premium 套餐（价格极度低廉，通常每月 < $1）；或者您也可以改用 ClouDNS 面向免费用户开放的免费 **Dynamic DNS (DDNS) 专用 URL 接口** 进行单条 A 记录的自动化 IP 更新。

### Q2：使用方向键选择菜单时没有反应或闪烁？
* **原因**：由于系统使用了 Windows 原生的 `msvcrt` 缓存库读取键盘扫描码，请确保您是在 **本地终端**（如 PowerShell、cmd.exe 或 Windows Terminal）中运行，而非某些 IDE 的内置非交互式仿真输出窗口中。

---

祝您使用愉快！如有任何优化建议，请随时在开发周期中进行调整。
