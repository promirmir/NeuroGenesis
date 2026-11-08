"""Operator-only local source training rights control; never infer permission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .memory import ExperienceMemory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Explicitly approve/revoke local training rights for a saved source revision")
    parser.add_argument("--db", required=True, type=Path)
    control = parser.add_mutually_exclusive_group(required=True)
    control.add_argument("--list", action="store_true", help="List recent source revisions")
    control.add_argument("--approve", type=int, metavar="SOURCE_ID")
    control.add_argument("--revoke", type=int, metavar="SOURCE_ID")
    parser.add_argument("--confirm-rights", action="store_true",
                        help="Operator confirms actual rights/permission for LOCAL model training")
    args = parser.parse_args(argv)
    memory = ExperienceMemory(args.db)
    if args.list:
        result = memory.knowledge_sources(limit=20)
    elif args.approve is not None:
        if args.confirm_rights is not True:
            parser.error("--confirm-rights required before approving a source")
        result = memory.set_source_training_rights(args.approve, True)
    else:
        result = memory.set_source_training_rights(args.revoke, False)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
