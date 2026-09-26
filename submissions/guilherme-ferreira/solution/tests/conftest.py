import pandas as pd
import pytest


@pytest.fixture
def posts_minimos():
    """Seis posts montados à mão, em duas semanas (a de 19/05/2025 tem 4 posts em 4 dias; a de 26/05, 2 posts em 2 dias)."""
    return pd.DataFrame(
        {
            "post_date": pd.to_datetime(
                ["2025-05-19 10:00", "2025-05-20 11:00", "2025-05-27 09:00", "2025-05-21 12:00", "2025-05-28 08:00", "2025-05-25 18:00"]
            ),
            "platform": ["TikTok", "TikTok", "YouTube", "YouTube", "TikTok", "YouTube"],
            "content_type": ["video", "video", "image", "text", "video", "image"],
            "content_category": ["beauty", "beauty", "lifestyle", "tech", "lifestyle", "beauty"],
            "language": ["English", "Chinese", "Hindi", "English", "Japanese", "English"],
            "content_description": ["hello", "你好", "hello", "x", "abc", "y"],
            "creator_id": ["c1", "c1", "c2", "c2", "c3", "c3"],
            "follower_count": [1000, 3000, 5000, 5000, 2000, 2000],
            "is_sponsored": [True, True, True, False, False, False],
            "sponsor_name": ["Acme", "Acme", "Beta", "Not sponsors", "Not sponsors", "Not sponsors"],
            "sponsor_category": ["cosmetics", "gaming", "food", "Not sponsors", "Not sponsors", "Not sponsors"],
            "disclosure_type": ["explicit", "implicit", "implicit", "none", "none", "none"],
            "disclosure_location": ["caption", "hashtags", "video", "none", "none", "none"],
            "views": [100, 110, 90, 100, 105, 95],
            "likes": [10, 12, 9, 10, 11, 9],
            "shares": [2, 2, 1, 2, 1, 2],
            "comments_count": [1, 2, 1, 1, 2, 1],
        }
    )
