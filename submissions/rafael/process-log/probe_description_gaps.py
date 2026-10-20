"""Checks the Kaggle description against the data: disclosure labels, units, timezone, coherence and tier mix."""
import sys

import pandas as pd

AD_MARKERS = {"ad", "ads", "sponsored", "sponsor", "partner", "paid", "collab"}
TIER_EDGES = [0, 1e4, 5e4, 1e5, 5e5, 1e7]


def has_ad_marker(hashtags: pd.Series) -> pd.Series:
    tags = hashtags.fillna("").str.lower().str.split(",")
    return tags.apply(lambda t: bool(AD_MARKERS & {x.strip().lstrip("#") for x in t}))


def main(path: str) -> None:
    df = pd.read_csv(path)
    sponsored = df[df.is_sponsored]
    print("sponsored × disclosure_type\n", pd.crosstab(df.is_sponsored, df.disclosure_type))
    print("implicit share:", round((sponsored.disclosure_type == "implicit").mean(), 3),
          "· video-only share:", round((sponsored.disclosure_location == "video").mean(), 3))
    print("ad marker in hashtags, by declared location\n",
          sponsored.assign(m=has_ad_marker(sponsored.hashtags)).groupby("disclosure_location").m.mean().round(4))
    print("ad marker in organic hashtags:", round(has_ad_marker(df[~df.is_sponsored].hashtags).mean(), 4))
    print("sponsor × content category\n", pd.crosstab(sponsored.content_category, sponsored.sponsor_category, normalize="index").round(3))
    print("content_length by type\n", df.groupby("content_type").content_length.describe()[["min", "50%", "max"]])
    print("platform × content_type\n", pd.crosstab(df.platform, df.content_type, normalize="index").round(3))
    print("platform × audience_location\n", pd.crosstab(df.platform, df.audience_location, normalize="index").round(3))
    print("language × audience_location\n", pd.crosstab(df.language, df.audience_location, normalize="index").round(3))
    print("post_date sample (no timezone):", df.post_date.head(2).tolist())
    print("follower tiers\n", pd.cut(df.follower_count, TIER_EDGES).value_counts(normalize=True).sort_index().round(3))
    print("comments_count min:", df.comments_count.min())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/raw/social_media_dataset.csv")
