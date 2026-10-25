"""List AI Studio models that support generateContent, to find the exact Gemma model id.

Usage: uv run python scripts/list_models.py [substring]   (for example: gemma)
"""

from __future__ import annotations

import sys

import httpx

from veriquery.common.config import Settings


def main() -> int:
    settings = Settings()
    if settings.gemini_api_key is None:
        sys.exit("GEMINI_API_KEY is not set (put it in .env)")
    needle = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    headers = {"x-goog-api-key": settings.gemini_api_key.get_secret_value()}
    token: str | None = None
    with httpx.Client(timeout=60.0) as client:
        while True:
            params: dict[str, str | int] = {"pageSize": 200}
            if token:
                params["pageToken"] = token
            response = client.get(url, headers=headers, params=params)
            if response.status_code >= 400:
                sys.exit(f"error {response.status_code}: {response.text[:300]}")
            data = response.json()
            for model in data.get("models", []):
                name = str(model.get("name", "")).removeprefix("models/")
                methods = model.get("supportedGenerationMethods", [])
                if "generateContent" in methods and needle in name.lower():
                    print(name)
            token = data.get("nextPageToken")
            if not token:
                return 0


if __name__ == "__main__":
    sys.exit(main())
