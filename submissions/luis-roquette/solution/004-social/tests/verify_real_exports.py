"""Independent stdlib-only audit: python tests/verify_real_exports.py RAW.csv evidence.csv."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median


def verify(raw_path: Path, evidence_path: Path) -> None:
    assert csv.field_size_limit() == 131072
    source_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    source = []
    physical = {}
    with raw_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        while True:
            line = reader.line_num + 1
            try:
                values = next(reader)
            except StopIteration:
                break
            item = dict(zip(header, values, strict=True))
            physical[item["id"]] = line
            for key in ("views", "likes", "shares", "comments_count", "follower_count"):
                item[key] = int(item[key])
            item["date"] = datetime.strptime(item["post_date"], "%m/%d/%y %I:%M %p")
            item["interactions"] = item["likes"] + item["shares"] + item["comments_count"]
            item["erv"] = 100 * item["interactions"] / item["views"] if item["views"] else None
            item["sponsored"] = item["is_sponsored"].lower() == "true"
            n = item["follower_count"]
            band = "0–9,999" if n < 10000 else "10,000–49,999" if n < 50000 else "50,000–99,999" if n < 100000 else "100,000–499,999" if n < 500000 else "500,000+"
            item["context"] = (item["platform"], item["content_type"], item["content_category"], band, item["date"].strftime("%Y-%m"))
            source.append(item)
    with evidence_path.open(newline="", encoding="utf-8") as handle:
        exported = list(csv.DictReader(handle))
    assert csv.field_size_limit() == 131072
    ids = {row["evidence_id"] for row in exported if row["record_type"] == "evidence"}
    restored = defaultdict(dict)
    for row in exported:
        if row["record_type"] != "source_ref":
            continue
        assert row["source_hash"] == source_hash and row["evidence_id"] in ids
        key = (row["evidence_id"], row["reference_role"])
        for index, fragment, line in zip(json.loads(row["reference_index"]), json.loads(row["source_row_id"]), json.loads(row["source_line"]), strict=True):
            previous = restored[key].get(index, ("", line))
            assert previous[1] == line
            restored[key][index] = (previous[0] + fragment, line)
    observed = set()
    links = 0
    for references in restored.values():
        assert sorted(references) == list(range(len(references)))
        for opaque, line in references.values():
            assert physical[opaque] == line
            observed.add(opaque)
            links += 1
    assert observed == set(physical)

    groups = defaultdict(list)
    for row in source:
        groups[row["context"]].append(row)

    def totals(rows):
        creators = {}
        for row in rows:
            creators[row["creator_id"]] = max(creators.get(row["creator_id"], 0), row["follower_count"])
        return {"views": sum(row["views"] for row in rows), "interactions": sum(row["interactions"] for row in rows), "followers": sum(creators.values())}

    pools = defaultdict(list)
    for context, rows in groups.items():
        sponsored = [row for row in rows if row["sponsored"]]
        if sponsored:
            pools[context[0]].append(totals(sponsored))

    def p95(values):
        values = sorted(values)
        position = (len(values) - 1) * .95
        low = int(position)
        value = values[low] + (values[math.ceil(position)] - values[low]) * (position - low)
        return value if value > 0 else max(values)

    denominators = {platform: {name: p95([row[name] for row in rows]) for name in ("views", "interactions", "followers")}
                    for platform, rows in pools.items()}
    reference = max(row["date"] for row in source).date()
    calculated = {}
    for context, rows in groups.items():
        arms = [[row for row in rows if row["sponsored"] == flag and row["erv"] is not None] for flag in (False, True)]
        if any(len(arm) < 30 or len({row["creator_id"] for row in arm}) < 5 for arm in arms):
            continue
        strengths, medians = [], []
        for arm in arms:
            creators = defaultdict(list)
            for row in arm:
                creators[row["creator_id"]].append(row["erv"])
            strengths.append(min(len(arm) / 100, 1) * min(len(creators) / 20, 1) * (1 - max(map(len, creators.values())) / len(arm)))
            medians.append(median(median(values) for values in creators.values()))
        values = totals(arms[1])
        impact = sum(min(values[key] / denominators[context[0]][key], 1) if denominators[context[0]][key] else 0 for key in values) / 3
        date = datetime.fromtimestamp(median(row["date"].timestamp() for row in arms[1]))
        recency = 2 ** (-(reference - date.date()).days / 7)
        calculated[context] = (100 * impact * min(strengths) * recency, medians[1] - medians[0], date, values)
    ranked = sorted(calculated, key=lambda context: (-calculated[context][0], -abs(calculated[context][1]), -calculated[context][2].timestamp(), context))
    unique = []
    for context in ranked:
        if context[:-1] not in [value[:-1] for value in unique]:
            unique.append(context)
    queue = [row for row in exported if row["record_type"] == "recommendation"]
    for row, context in zip(queue, unique, strict=True):
        assert tuple(json.loads(row["context"])[key] for key in ("platform", "content_type", "content_category", "follower_band", "period_month")) == context
        score, delta, _, values = calculated[context]
        assert math.isclose(float(row["priority"]), score, rel_tol=1e-12)
        assert math.isclose(float(row["delta_erv_pp"]), delta, abs_tol=1e-12)
        assert json.loads(row["priority_values"]) == values
        print("priority", row["evidence_id"], context, score, "delta", delta)

    for dimension in ("audience_age_distribution", "audience_gender_distribution", "audience_location"):
        cells = defaultdict(list)
        for row in source:
            cells[(*row["context"], row["sponsored"], row[dimension])].append(row)
        strata = {key[:-1] for key in cells}
        eligible = {key: rows for key, rows in cells.items() if sum(row["erv"] is not None for row in rows) >= 30 and len({row["creator_id"] for row in rows if row["erv"] is not None}) >= 5}
        eligible_counts = Counter(key[:-1] for key in eligible)
        comparable = {key for key, count in eligible_counts.items() if count >= 2}
        covered = {row["id"] for key, rows in eligible.items() if key[:-1] in comparable for row in rows if row["erv"] is not None}
        expected = dict(total_strata=len(strata), eligible_strata=len(comparable), total_cells=len(cells), eligible_cells=len(eligible),
                        max_cell_defined_rates=max(sum(row["erv"] is not None for row in rows) for rows in cells.values()), covered_posts=len(covered))
        evidence = next(json.loads(row["statistics"]) for row in exported if row["record_type"] == "evidence" and row["evidence_id"].startswith("audience-overview-") and json.loads(row["statistics"])["dimension"] == dimension)
        assert all(evidence[key] == value for key, value in expected.items())
        print("audience", dimension, expected)
    print("source_roundtrip", len(observed), "links", links, "records", len(exported), "max_field", max(len(value) for row in exported for value in row.values()), "default_limit", csv.field_size_limit())
    print("record_counts", dict(Counter(row["record_type"] for row in exported)))


if __name__ == "__main__":
    verify(Path(sys.argv[1]), Path(sys.argv[2]))
