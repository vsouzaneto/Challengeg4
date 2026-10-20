"""CLI: `python -m leadscorer <comando>`."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import cli_text, data, policy, views
from .errors import LeadScorerError
from .fmt import fmt_int


def check_data(raw_dir: Path) -> int:
    dataset = data.load(raw_dir)
    frame = dataset.opportunities
    audited = sum(dataset.hashes[t] == policy.AUDITED_SHA256[t] for t in data.TABLES)
    text = cli_text.CHECK_DATA
    print(text["folder"].format(folder=data.display_path(raw_dir)))
    print(text["hash"].format(audited=audited, total=len(data.TABLES)))
    if not dataset.audited:
        print(cli_text.DATA_WARNING)
    print(text["joins"])
    for step in dataset.steps:
        gap = f"   {cli_text.JOIN_GAPS[step.gap]}: {fmt_int(step.gap_count)}" if step.gap else ""
        print(f"  {cli_text.JOIN_STEPS[step.table]:<16} {fmt_int(step.rows):>6}{gap}")
    print(text["unmatched"].format(count=fmt_int(dataset.unmatched_without_map)))
    stages = frame["deal_stage"].value_counts()
    parts = " + ".join(f"{fmt_int(stages.get(s, 0))} {s}" for s in policy.CLOSED_STAGES + policy.OPEN_STAGES)
    print(text["opportunities"].format(total=fmt_int(len(frame)), parts=parts))
    is_open = frame["deal_stage"].isin(policy.OPEN_STAGES)
    print(text["open"].format(count=fmt_int(is_open.sum())))
    return 0


def render_item(entry: Dict[str, Any], indent: str) -> str:
    age = "—" if entry["age_days"] is None else f"{entry['age_days']} d"
    engaged = "—" if entry["engage_date"] is None else cli_text.iso_date(entry["engage_date"])
    price = "—" if entry["sales_price"] is None else fmt_int(entry["sales_price"])
    line = (f"{indent}{entry['opportunity_id']:<10}{entry['product'] or '—':<16}{cli_text.client_text(entry):<26}"
            f"{price:>8}   {engaged:<12}{age:>6}")
    missing = entry["missing_field"]
    return f"{line}   ({cli_text.missing_short(missing)})" if missing else line


def render_list(payload: Dict[str, Any]) -> str:
    """Lista do vendedor montada só com chaves, códigos e números do payload."""
    summary, meta = payload["summary"], payload["meta"]
    lines = [] if meta["audited"] else [cli_text.DATA_WARNING]
    lines += [
        f"{payload['seller']} · {cli_text.data_label(meta)}",
        f"{summary['total']} {cli_text.OPEN} = {cli_text.summary_counts(payload)}",
    ]
    if payload["empty"]:
        return "\n".join(lines + ["", cli_text.empty_text(payload["empty"])])
    empty_groups = cli_text.empty_groups_text(payload)
    if empty_groups:
        lines.append(empty_groups)
    if summary["without_account"]:
        lines.append(f"{cli_text.NOTE}: {cli_text.account_warning(summary)}. {cli_text.ACCOUNT_NOTE}")
    lines.append(cli_text.legend_text(payload["ordering"]))
    widths = (10, 16, 26, 8, 12, 6)
    names = cli_text.COLUMNS
    header = (f"      {names[0]:<{widths[0]}}{names[1]:<{widths[1]}}{names[2]:<{widths[2]}}{names[3]:>{widths[3]}}   "
              f"{names[4]:<{widths[4]}}{names[5]:>{widths[5]}}")

    for group in payload["groups"]:
        lines += ["", f"{cli_text.GROUP_LABELS[group['state']].upper()} ({group['count']})"]
        if not group["items"]:
            lines.append(f"  {cli_text.empty_text(group['empty'])}")
            continue
        lines += [f"  {cli_text.NEXT_STEP}: {cli_text.action_text(group['next_action'])}", header]
        band_counts = Counter(cli_text.band_title(entry["value_band"]) for entry in group["items"])
        band = product = None
        for entry in group["items"]:
            title = cli_text.band_title(entry["value_band"])
            if title != band:
                band, product = title, None
                lines.append(f"  {band} ({band_counts[band]})")
            tied = entry["tie_size"] > 1 and entry["sales_price"] is not None
            if tied and entry["product"] != product:
                lines.append(f"    ▸ {cli_text.tie_text(entry['tie_size'], entry['product'], entry['sales_price'])}")
            product = entry["product"]
            lines.append(render_item(entry, "        " if tied else "      "))
    return "\n".join(lines)


def render_detail(detail: Dict[str, Any]) -> str:
    """"Por que está aqui" de uma oportunidade, montado só com os códigos do item."""
    entry, meta = detail["item"], detail["meta"]
    lines = [] if meta["audited"] else [cli_text.DATA_WARNING]
    lines += [
        f"{entry['opportunity_id']} · {entry['product'] or cli_text.NO_PRODUCT} · {cli_text.client_text(entry)} · "
        f"{detail['seller']}",
        cli_text.data_label(meta),
        "",
        cli_text.WHY_HERE,
    ]
    lines += [f"  • {cli_text.reason_text(reason)}" for reason in entry["reasons"]]
    tie = cli_text.tie_note(entry)
    if tie:
        lines.append(f"  • {tie}")
    age = cli_text.age_context(entry["age_days"], meta)
    if age:
        lines += ["", cli_text.AGE_CONTEXT_TITLE, f"  {age}", f"  {cli_text.AGE_CONTEXT_NOTE}"]
    lines += ["", f"{cli_text.NEXT_STEP}: {cli_text.action_text(entry['next_action'], entry['account'])}"]
    lines += ["", cli_text.SUGGESTIONS_TITLE, f"  {cli_text.SUGGESTIONS_INTRO}"]
    lines += [f"  • {text}" for text in cli_text.suggestions_for(entry)]
    lines += ["", f"  {cli_text.LIMITS_NOTE}"]
    return "\n".join(lines)


def list_pipeline(raw_dir: Path, seller: str, as_of: Optional[str], as_json: bool) -> int:
    payload = views.seller_pipeline(data.load(raw_dir), seller, as_of)
    print(json.dumps(payload, ensure_ascii=False, indent=2) if as_json else render_list(payload))
    return 0


def explain_opportunity(raw_dir: Path, opportunity_id: str, as_of: Optional[str], as_json: bool) -> int:
    detail = views.opportunity_detail(data.load(raw_dir), opportunity_id, as_of)
    print(json.dumps(detail, ensure_ascii=False, indent=2) if as_json else render_detail(detail))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    help_ = cli_text.HELP
    parser = argparse.ArgumentParser(prog="python -m leadscorer")
    parser.add_argument("--raw", type=Path, default=policy.RAW_DIR, help=help_["raw"])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check-data", help=help_["check-data"])
    listing = commands.add_parser("list", help=help_["list"])
    listing.add_argument("--seller", required=True, help=help_["seller"])
    listing.add_argument("--as-of", help=help_["as-of"])
    listing.add_argument("--json", action="store_true", help=help_["json"])
    explaining = commands.add_parser("explain", help=help_["explain"])
    explaining.add_argument("--id", required=True, dest="opportunity_id", help=help_["id"])
    explaining.add_argument("--as-of", help=help_["as-of"])
    explaining.add_argument("--json", action="store_true", help=help_["json"])
    args = parser.parse_args(argv)

    try:
        if args.command == "check-data":
            return check_data(args.raw)
        if args.command == "list":
            return list_pipeline(args.raw, args.seller, args.as_of, args.json)
        if args.command == "explain":
            return explain_opportunity(args.raw, args.opportunity_id, args.as_of, args.json)
    except LeadScorerError as error:
        # Nenhuma lista parcial: o erro sai sozinho, com a mensagem para o usuário.
        print(f"{cli_text.ERROR}: {error}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
