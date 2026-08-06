"""Interactive REPL for the live demo.

Usage:
    python -m app.cli --user cust_ns_01 --tenant northstar_bank
    python -m app.cli --list-users

Type a question and press Enter. Type `exit` to quit.
"""
from __future__ import annotations

import argparse

from app.bootstrap import build_pipeline
from app.display import print_result


def list_users(registry) -> None:
    print("Known users (user_id | tenant_id | role | display_name):")
    for user_id, user in registry._users.items():  # demo-only introspection
        print(f"  {user_id:16s} | {user.tenant_id:22s} | {user.role.value:18s} | {user.display_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Secure Banking RAG demo — interactive CLI")
    parser.add_argument("--user", help="user_id to act as, e.g. cust_ns_01")
    parser.add_argument("--tenant", help="tenant_id claimed for this session, e.g. northstar_bank")
    parser.add_argument("--list-users", action="store_true", help="list available demo users and exit")
    args = parser.parse_args()

    pipeline, registry = build_pipeline()

    if args.list_users or not (args.user and args.tenant):
        list_users(registry)
        if not (args.user and args.tenant):
            print("\nRe-run with --user <id> --tenant <id> to start the REPL.")
        return

    print(f"Ingested chunk counts: {pipeline.ingested_chunk_counts}")
    print(f"Acting as user_id={args.user}, claimed tenant_id={args.tenant}. Type 'exit' to quit.\n")

    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            break

        result = pipeline.ask(args.user, args.tenant, query)
        print_result(result, actor_label="live")


if __name__ == "__main__":
    main()
