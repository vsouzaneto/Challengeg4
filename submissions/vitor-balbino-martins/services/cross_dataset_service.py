import csv
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean

from core.config import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


class CrossDatasetService:
    @staticmethod
    def _read(filename):
        path = Path(__file__).resolve().parents[1] / settings.RAG_ASSETS_DIR / filename
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file)), path

    @staticmethod
    def _text(row, fields):
        return " ".join(row.get(field, "") or "" for field in fields)

    @classmethod
    def analyze_satisfaction(cls, metrics_dataset="customer_support_tickets.csv", text_dataset="all_tickets_processed_improved_v3.csv"):
        tickets, ticket_path = cls._read(metrics_dataset)
        texts, text_path = cls._read(text_dataset)
        

        text_values = [cls._text(row, ("Document",)) for row in texts]
        ticket_values = [cls._text(row, ("Ticket Subject", "Ticket Description", "Resolution")) for row in tickets]
        vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=2, max_features=100000)
        vectorizer.fit(text_values + ticket_values)
        text_matrix = vectorizer.transform(text_values)
        ticket_matrix = vectorizer.transform(ticket_values)
        matcher = NearestNeighbors(n_neighbors=1, metric="cosine", algorithm="brute").fit(text_matrix)
        distances, indexes = matcher.kneighbors(ticket_matrix)
        groups = defaultdict(list)
        matched = []
        for ticket, distance, index in zip(tickets, distances[:, 0], indexes[:, 0]):
            rating = cls._number(ticket.get("Customer Satisfaction Rating"))
            if rating is None: continue
            topic = texts[index].get("Topic_group") or "unknown"
            record = {"ticket_id": ticket.get("Ticket ID"), "rating": rating, "similarity": round(1 - float(distance), 4), "topic": topic, "subject": ticket.get("Ticket Subject"), "document_source": f"{text_path.name}:row {index + 2}"}
            groups[topic].append(record)
            matched.append(record)
        summaries = []
        for topic, records in groups.items():
            summaries.append({"topic": topic, "tickets": len(records), "avg_rating": round(mean(r["rating"] for r in records), 3), "low_rating_count": sum(r["rating"] <= 2 for r in records), "high_rating_count": sum(r["rating"] >= 4 for r in records), "evidence": sorted(records, key=lambda r: r["rating"])[:3]})
        summaries.sort(key=lambda item: item["avg_rating"])
        return {"crossing": {"metrics_dataset": ticket_path.name, "text_dataset": text_path.name, "method": "TF-IDF nearest document by cosine similarity", "matched_tickets": len(matched)}, "lowest_satisfaction": summaries[:5], "highest_satisfaction": list(reversed(summaries[-5:])), "topics": summaries}

    @staticmethod
    def _number(value):
        match = re.search(r"\d+(?:\.\d+)?", value or "")
        return float(match.group()) if match else None
