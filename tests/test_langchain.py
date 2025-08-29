url = "https://app.galileo.ai/api/galileo/v2/projects/51ad7429-4106-4850-a612-da2425faf34c/traces/search"
import requests
import os

assert requests.post(
    url,
    json={
        "log_stream_id": "8495fe11-1fb8-44e0-9c83-b9e604aced5f",
        "starting_token": 0,
        "limit": 50,
        "filters": [
            {
                "column_id": "created_at",
                "type": "date",
                "operator": "lte",
                "value": "2025-08-29T15:51:59.000Z",
            },
            {
                "column_id": "created_at",
                "type": "date",
                "operator": "gte",
                "value": "2025-07-30T15:51:59.000Z",
            },
        ],
        "sort": {"sort_type": "column", "column_id": "created_at", "ascending": False},
        "truncate_fields": True,
    },
    headers={"Galileo-Api-Key": os.getenv("GALILEO_API_KEY")},
    timeout=10,
).json()["records"][0]["is_complete"]
