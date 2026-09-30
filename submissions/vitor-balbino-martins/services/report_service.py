import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from core.config import settings
from services.agents.ticket_consolidator import TicketConsolidationAgent
from services.agents.ticket_extractor import TicketExtractionAgent
from services.report_parser import ReportParser


class SupportReportService:
    @staticmethod
    def _number(value):
        
        timestamp = re.search(r"\d{4}-\d{2}-\d{2}\s+(\d{1,2}):(\d{2})(?::(\d{2}))?", value or "")
        if timestamp:
            return float(timestamp.group(1)) + float(timestamp.group(2)) / 60 + float(timestamp.group(3) or 0) / 3600
        match = re.search(r"\d+(?:\.\d+)?", value or "")
        if not match: return None
        number = float(match.group())
        unit = (value or "").lower()
        if "minute" in unit or "min" in unit: return number / 60
        if "day" in unit or "dia" in unit: return number * 24
        return number

    @classmethod
    def _load(cls, filename):
        path = Path(__file__).resolve().parents[1] / settings.RAG_ASSETS_DIR / filename
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle)), path

    @classmethod
    def _metrics(cls, rows, hourly_cost=None):
        def values(field):
            return [cls._number(r.get(field)) for r in rows if cls._number(r.get(field)) is not None]
        resolution, first_response, satisfaction = values("Time to Resolution"), values("First Response Time"), values("Customer Satisfaction Rating")
        def counts(field): return dict(Counter(r.get(field) or "unknown" for r in rows))
        def grouped(fields, metric="Time to Resolution"):
            groups = defaultdict(list)
            for row in rows:
                number = cls._number(row.get(metric))
                if number is not None: groups[tuple(row.get(f) or "unknown" for f in fields)].append(number)
            return [{"dimensions": dict(zip(fields, key)), "tickets": len(v), "avg": round(mean(v), 3)} for key, v in sorted(groups.items(), key=lambda item: mean(item[1]), reverse=True)]
        def correlation(a, b):
            pairs = [(cls._number(r.get(a)), cls._number(r.get(b))) for r in rows]
            pairs = [(x, y) for x, y in pairs if x is not None and y is not None]
            if len(pairs) < 2: return None
            ax, by = mean(x for x, _ in pairs), mean(y for _, y in pairs)
            den = (sum((x-ax)**2 for x, _ in pairs) * sum((y-by)**2 for _, y in pairs)) ** 0.5
            return round(sum((x-ax)*(y-by) for x, y in pairs) / den, 4) if den else None
        combinations = grouped(["Ticket Channel", "Ticket Priority", "Ticket Type"])
        benchmark = min((item["avg"] for item in combinations), default=0)
        excess_hours = sum(max(0, (cls._number(r.get("Time to Resolution")) or 0) - benchmark) for r in rows)
        waste = {"benchmark_resolution": benchmark, "recoverable_hours": round(excess_hours, 2)}
        if hourly_cost is not None: waste["estimated_cost"] = round(excess_hours * hourly_cost, 2)
        return {"ticket_count": len(rows), "avg_resolution": round(mean(resolution), 3) if resolution else None,
                "avg_first_response": round(mean(first_response), 3) if first_response else None,
                "avg_satisfaction": round(mean(satisfaction), 3) if satisfaction else None,
                "channels": counts("Ticket Channel"), "priorities": counts("Ticket Priority"), "ticket_types": counts("Ticket Type"),
                "satisfaction_by_channel": grouped(["Ticket Channel"], "Customer Satisfaction Rating"),
                "satisfaction_by_priority": grouped(["Ticket Priority"], "Customer Satisfaction Rating"),
                "satisfaction_by_type": grouped(["Ticket Type"], "Customer Satisfaction Rating"),
                "correlations_with_satisfaction": {"first_response": correlation("First Response Time", "Customer Satisfaction Rating"), "resolution": correlation("Time to Resolution", "Customer Satisfaction Rating")},
                "worst_combinations": combinations[:10], "waste": waste}

    @classmethod
    def generate(cls, dataset="customer_support_tickets.csv", chunk_size=100, hourly_cost=None):
        rows, path = cls._load(dataset)
        metrics = cls._metrics(rows, hourly_cost)
        extractions = []
        sources = [{"file": path.name, "rows": f"2-{len(rows)+1}", "records": len(rows), "basis": "full CSV"}]
        for start in range(0, len(rows), chunk_size):
            chunk = rows[start:start + chunk_size]
            tickets = [{k: r.get(k) for k in ("Ticket ID", "Ticket Subject", "Ticket Description", "Ticket Channel", "Ticket Priority", "Ticket Type", "Time to Resolution", "Customer Satisfaction Rating")} for r in chunk]
            result = TicketExtractionAgent().run({"tickets": tickets})
            extractions.append({"chunk": start // chunk_size + 1, "rows": f"{start+2}-{start+len(chunk)+1}", "result": result})
        consolidated = TicketConsolidationAgent().run({"metrics": metrics, "chunk_extractions": extractions})
        audit = ReportParser.parse(dataset, metrics, extractions, consolidated, sources)
        return {"dataset": dataset, "metrics": metrics, "extraction": {"chunks": len(extractions), "items": extractions}, "consolidation": consolidated, "audit": audit}
