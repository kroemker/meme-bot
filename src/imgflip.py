import requests

GET_MEMES_URL = "https://api.imgflip.com/get_memes"
CAPTION_URL = "https://api.imgflip.com/caption_image"


def get_templates(limit: int = 100) -> list[dict]:
    response = requests.get(GET_MEMES_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(f"imgflip get_memes failed: {data}")
    return data["data"]["memes"][:limit]


def caption_image(template_id: str, texts: list[str], username: str, password: str) -> str:
    payload = {
        "template_id": template_id,
        "username": username,
        "password": password,
    }
    for i, text in enumerate(texts):
        payload[f"text{i}"] = text

    response = requests.post(CAPTION_URL, data=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(f"imgflip caption_image failed: {data.get('error_message')}")
    return data["data"]["url"]
