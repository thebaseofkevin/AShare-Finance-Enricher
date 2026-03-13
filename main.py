"""项目统一入口：选择执行 baostock_fetch 或 yahoo_enrich。"""
import argparse
import sys
from typing import Optional

import baostock_fetch
import yahoo_enrich


def _run_yahoo(input_db: str, limit: Optional[int]) -> None:
    """复用 yahoo_enrich 的 CLI，通过 sys.argv 透传参数。"""
    argv = ["yahoo_enrich.py", "--input-db", input_db]
    if limit is not None:
        argv += ["--limit", str(limit)]
    old_argv = sys.argv
    try:
        sys.argv = argv
        yahoo_enrich.main()
    finally:
        sys.argv = old_argv


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "AShare-Finance-Enricher 统一入口。\n"
            "可选择执行：\n"
            "1) baostock：拉取 A 股基础信息 -> 生成 {日期}_stocks_name.db\n"
            "2) yahoo：读取上一步生成的数据库 -> 补充 Yahoo 指标 -> 输出 YYYY-MM-DD_HHMMSS_stocks_info.db"
        ),
        epilog=(
            "示例：\n"
            "  python main.py baostock\n"
            "  python main.py yahoo --input-db 2026-03-13_stocks_name.db\n"
            "  python main.py yahoo --input-db 2026-03-13_stocks_name.db --limit 100\n"
            "\n"
            "提示：若提示 yfinance 未安装，请先执行：pip install -r requirements.txt"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "baostock",
        help="拉取 A 股基础信息并保存到 SQLite",
        description=(
            "拉取 A 股基础信息并保存到 SQLite。\n"
            "输出：{日期}_stocks_name.db（表名：stocks）"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    yahoo_parser = subparsers.add_parser(
        "yahoo",
        help="用 Yahoo Finance 补充指标并输出新库",
        description=(
            "读取输入数据库（来自 baostock），补充 Yahoo Finance 指标并输出新库。\n"
            "输出：YYYY-MM-DD_HHMMSS_stocks_info.db（表名：stocks）"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    yahoo_parser.add_argument(
        "--input-db",
        required=True,
        help="输入 SQLite db 文件名，例如 2026-03-13_stocks_name.db",
    )
    yahoo_parser.add_argument(
        "--limit",
        type=int,
        help="仅处理前 N 行（用于测试），例如 --limit 100",
    )

    args = parser.parse_args()

    if args.command == "baostock":
        baostock_fetch.main()
    elif args.command == "yahoo":
        _run_yahoo(args.input_db, args.limit)
    else:
        parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
