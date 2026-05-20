import os
import sys
import msvcrt
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, IntPrompt

from core.api_client import ClouDNSClient
from core.config_manager import ConfigManager
from core.dns import DNSManager

console = Console()

def clear_screen():
    """Clears the console screen."""
    os.system("cls" if os.name == "nt" else "clear")

def select_option(title: str, options: List[str], subtitle: str = "使用 ↑/↓ 方向键选择，Enter 键确认") -> int:
    """
    Renders an elegant interactive selection menu using Rich Live and Windows msvcrt.
    Supports Up/Down arrows to navigate and Enter to select. Esc returns -1.
    """
    selected_idx = 0
    
    def generate_menu_renderable() -> Panel:
        menu_text = Text()
        for idx, option in enumerate(options):
            if idx == selected_idx:
                menu_text.append(f"  ➜  {option}\n", style="bold cyan")
            else:
                menu_text.append(f"     {option}\n", style="dim white")
        return Panel(
            menu_text,
            title=f"[bold green]✨ {title} ✨[/bold green]",
            subtitle=f"[dim yellow]⌨️ {subtitle}[/dim yellow]",
            border_style="cyan",
            expand=False
        )

    with Live(generate_menu_renderable(), console=console, auto_refresh=False) as live:
        while True:
            live.update(generate_menu_renderable(), refresh=True)
            
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in (b'\x00', b'\xe0'):
                    arrow = msvcrt.getch()
                    if arrow == b'H':  # Up Arrow
                        selected_idx = (selected_idx - 1) % len(options)
                    elif arrow == b'P':  # Down Arrow
                        selected_idx = (selected_idx + 1) % len(options)
                elif key in (b'\r', b'\n'):  # Enter
                    break
                elif key == b'\x1b':  # Esc
                    return -1
                    
    return selected_idx

class DNSHECLI:
    """
    Rich CLI UI controller for ClouDNS record management.
    """
    def __init__(self):
        self.config_manager = ConfigManager()
        self.client: Optional[ClouDNSClient] = None
        self.dns_manager: Optional[DNSManager] = None
        self.selected_profile_name: str = ""

    def run(self):
        clear_screen()
        console.print(Panel.fit(
            "[bold cyan]ClouDNS DNS 智能 API 管理终端[/bold cyan]\n"
            "[dim]使用 Rich + Native 键盘交互，快速执行 DNS CRUD 解析操作[/dim]",
            border_style="magenta"
        ))

        # 1. 认证加载
        profiles = self.config_manager.get_profiles()
        api_base_url = self.config_manager.get_api_base_url()

        if not profiles:
            console.print("[bold yellow][!] 未在本地 users.json 查找到任何 API Profile。[/bold yellow]")
            auth_id = Prompt.ask("[bold green]请输入 ClouDNS Auth ID (纯数字)[/bold green]").strip()
            auth_password = Prompt.ask("[bold green]请输入 ClouDNS API Password[/bold green]", password=True).strip()
            if not auth_id or not auth_password:
                console.print("[bold red][✘] Auth ID 或 Password 不能为空，程序退出。[/bold red]")
                return
            
            # 创建临时 Profile
            self.client = ClouDNSClient(auth_id, auth_password, api_base_url)
            self.selected_profile_name = "Manual Input"
        else:
            profile_names = list(profiles.keys())
            if len(profile_names) == 1:
                self.selected_profile_name = profile_names[0]
            else:
                idx = select_option("请选择 API 账户 Profile", profile_names)
                if idx == -1:
                    console.print("[bold yellow][!] 已取消选择，使用默认首个 Profile。[/bold yellow]")
                    self.selected_profile_name = profile_names[0]
                else:
                    self.selected_profile_name = profile_names[idx]

            profile = profiles[self.selected_profile_name]
            auth_id = profile.get("auth_id", "")
            auth_password = profile.get("auth_password", "")
            
            self.client = ClouDNSClient(auth_id, auth_password, api_base_url)
            self.config_manager.update_last_used(self.selected_profile_name)

        self.dns_manager = DNSManager(self.client)
        console.print(f"[bold green][✔] 成功激活账号：{self.selected_profile_name} (Auth ID: {auth_id})[/bold green]\n")

        # 2. 引导域名选择
        domain_name = ""
        domains = []
        if profiles and self.selected_profile_name in profiles:
            profile = profiles[self.selected_profile_name]
            domains = profile.get("domain_name", [])
            
        if isinstance(domains, str):
            domains = [domains]
            
        if not domains:
            domain_name = Prompt.ask("[bold green]请输入要操作的域名 (例如: example.com)[/bold green]").strip()
        elif len(domains) == 1:
            domain_name = domains[0]
            console.print(f"[bold green][✔] 自动选择管理域名：[cyan]{domain_name}[/cyan][/bold green]")
        else:
            domain_options = list(domains) + ["➕ 手动输入其它域名"]
            idx = select_option("请选择要操作的主域名", domain_options)
            if idx == -1 or idx == len(domains):
                domain_name = Prompt.ask("[bold green]请输入要操作的域名 (例如: example.com)[/bold green]").strip()
            else:
                domain_name = domains[idx]
                console.print(f"[bold green][✔] 已选择域名：[cyan]{domain_name}[/cyan][/bold green]")
                
        if not domain_name:
            console.print("[bold red][✘] 域名不能为空。[/bold red]")
            return


        # 3. 循环交互主菜单
        menu_options = [
            "📋 列出 DNS 解析记录 (List Records)",
            "➕ 添加 DNS 解析记录 (Add Record)",
            "✏️ 修改 DNS 解析记录 (Modify Record)",
            "❌ 删除 DNS 解析记录 (Delete Record)",
            "🚪 退出程序 (Exit)"
        ]

        while True:
            # 隔开界面并提供清晰的选单
            console.print("\n" + "—" * 60)
            choice_idx = select_option(f"管理域名: {domain_name}", menu_options)
            
            if choice_idx == 0:
                self.list_records(domain_name)
            elif choice_idx == 1:
                self.add_record(domain_name)
            elif choice_idx == 2:
                self.modify_record(domain_name)
            elif choice_idx == 3:
                self.delete_record(domain_name)
            elif choice_idx == 4 or choice_idx == -1:
                console.print("\n[bold magenta]👋 感谢使用，再见！[/bold magenta]")
                break

    def list_records(self, domain_name: str) -> Optional[List[Dict[str, Any]]]:
        """Lists DNS records in a stunning Rich Table."""
        console.print(f"\n[*] 正在获取 [cyan]{domain_name}[/cyan] 的最新解析记录...")
        res = self.dns_manager.list_records(domain_name)
        
        if not res["success"]:
            console.print(f"[bold red][✘] 获取失败: {res.get('message')}[/bold red]")
            return None
            
        records = res["records"]
        if not records:
            console.print(Panel("[yellow]该域名下暂无任何解析记录！[/yellow]", border_style="yellow"))
            return []
            
        table = Table(
            title=f"📋 [bold cyan]{domain_name}[/bold cyan] 解析记录表", 
            border_style="bright_blue",
            header_style="bold magenta",
            show_lines=True
        )
        table.add_column("Record ID", style="green", width=12)
        table.add_column("Type", style="bold yellow", width=8, justify="center")
        table.add_column("Host (主机)", style="cyan", width=18)
        table.add_column("Points To (记录值/目标)", style="white")
        table.add_column("TTL", style="blue", justify="center", width=8)

        for r in records:
            # For MX/SRV, render priority nicely
            value = r.get("record", "")
            if r.get("priority"):
                value = f"[bold green][Prio: {r.get('priority')}][/bold green] {value}"
                
            table.add_row(
                str(r.get("id", "")),
                str(r.get("type", "")),
                str(r.get("host", "")),
                value,
                str(r.get("ttl", ""))
            )
            
        console.print(table)
        return records

    def add_record(self, domain_name: str):
        """Adds a new DNS record with beautiful color prompt wizard."""
        console.print(Panel("[bold green]➕ 创建新解析记录[/bold green]", border_style="green"))
        
        # Select type
        types = ["A", "AAAA", "CNAME", "TXT", "MX", "NS", "SRV", "CAA"]
        type_idx = select_option("请选择要创建的记录类型", types)
        if type_idx == -1:
            console.print("[yellow][!] 已取消添加记录。[/yellow]")
            return
        record_type = types[type_idx]

        host = Prompt.ask("[bold green]主机名/子域名[/bold green] (例如 'www'，若为根域名请输入 '@')").strip()
        record = Prompt.ask("[bold green]记录值[/bold green] (例如 IP 地址 / 别名域名 / TXT 文本值)").strip()
        ttl = IntPrompt.ask("[bold green]TTL (秒数)[/bold green]", default=3600)

        priority = None
        if record_type in ["MX", "SRV"]:
            priority = IntPrompt.ask("[bold green]优先级 (Priority)[/bold green]", default=10)

        console.print(f"\n[*] 正在添加记录: [cyan]{host or '@'} {record_type} -> {record}[/cyan] ...")
        res = self.dns_manager.add_record(domain_name, record_type, host, record, ttl, priority)
        
        if res["success"]:
            console.print(Panel(
                f"[bold green]✔ 解析记录创建成功！[/bold green]\n"
                f"添加详情: [cyan]{host or '@'} {record_type} -> {record} (TTL: {ttl})[/cyan]", 
                border_style="green"
            ))
        else:
            console.print(f"[bold red][✘] 创建失败: {res.get('message')}[/bold red]")

    def modify_record(self, domain_name: str):
        """Modifies a DNS record, listing existing records for interactive picking."""
        console.print(Panel("[bold yellow]✏️ 修改现有解析记录[/bold yellow]", border_style="yellow"))
        
        # Optional: Auto-fetch first to show valid choices
        records = self.list_records(domain_name)
        if not records:
            return

        record_id = Prompt.ask("\n[bold green]请输入要修改的 Record ID[/bold green]").strip()
        if not record_id:
            console.print("[yellow][!] 记录 ID 不能为空。[/yellow]")
            return

        # Find match to pre-fill prompts
        match = next((r for r in records if str(r.get("id")) == record_id), None)
        if not match:
            console.print(f"[bold red][✘] 未在列表中找到 Record ID 为 {record_id} 的解析记录，请仔细核对。[/bold red]")
            return

        console.print(f"\n[*] 正在修改记录 [cyan]{match.get('host')} {match.get('type')} -> {match.get('record')}[/cyan]")
        
        host = Prompt.ask(f"[bold green]新主机名 (当前: '{match.get('host')}')[/bold green]", default=match.get("host")).strip()
        record = Prompt.ask(f"[bold green]新记录值 (当前: '{match.get('record')}')[/bold green]", default=match.get("record")).strip()
        
        try:
            curr_ttl = int(match.get("ttl", 3600))
        except ValueError:
            curr_ttl = 3600
        ttl = IntPrompt.ask(f"[bold green]新 TTL (当前: {curr_ttl})[/bold green]", default=curr_ttl)

        priority = None
        if match.get("type") in ["MX", "SRV"]:
            curr_prio = match.get("priority", 10)
            priority = IntPrompt.ask(f"[bold green]新优先级 (当前: {curr_prio})[/bold green]", default=curr_prio)

        console.print(f"\n[*] 正在提交更新 [cyan]ID: {record_id}[/cyan] ...")
        res = self.dns_manager.modify_record(domain_name, record_id, host, record, ttl, priority)
        
        if res["success"]:
            console.print(Panel(
                f"[bold green]✔ 解析记录更新成功！[/bold green]\n"
                f"更新详情: [cyan]{host or '@'} {match.get('type')} -> {record} (TTL: {ttl})[/cyan]", 
                border_style="green"
            ))
        else:
            console.print(f"[bold red][✘] 更新失败: {res.get('message')}[/bold red]")

    def delete_record(self, domain_name: str):
        """Deletes a DNS record with strong prompt verification."""
        console.print(Panel("[bold red]❌ 删除解析记录[/bold red]", border_style="red"))
        
        records = self.list_records(domain_name)
        if not records:
            return

        record_id = Prompt.ask("\n[bold green]请输入要删除的 Record ID[/bold green]").strip()
        if not record_id:
            return

        match = next((r for r in records if str(r.get("id")) == record_id), None)
        if not match:
            console.print(f"[bold red][✘] 未在列表中找到 Record ID 为 {record_id} 的解析记录。[/bold red]")
            return

        # Confirm
        confirm = Prompt.ask(
            f"[bold red]确定要彻底删除记录 [yellow]{match.get('host') or '@'} {match.get('type')} -> {match.get('record')}[/yellow] 吗？[/bold red]",
            choices=["y", "n"],
            default="n"
        )
        
        if confirm == "y":
            console.print(f"[*] 正在请求删除记录 ID [cyan]{record_id}[/cyan]...")
            res = self.dns_manager.delete_record(domain_name, record_id)
            if res["success"]:
                console.print(Panel(f"[bold green]✔ 记录 ID {record_id} 删除成功！[/bold green]", border_style="green"))
            else:
                console.print(f"[bold red][✘] 删除失败: {res.get('message')}[/bold red]")
        else:
            console.print("[yellow][!] 操作已取消。[/yellow]")
