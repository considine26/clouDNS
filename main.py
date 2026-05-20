from core.cli import DNSHECLI

def main():
    try:
        app = DNSHECLI()
        app.run()
    except KeyboardInterrupt:
        print("\n[!] 用户强制退出。再见！")

if __name__ == "__main__":
    main()
