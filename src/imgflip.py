import requests

GET_MEMES_URL = "https://api.imgflip.com/get_memes"
CAPTION_URL = "https://api.imgflip.com/caption_image"


def get_templates(limit: int = 30) -> list[dict]:
    response = requests.get(GET_MEMES_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(f"imgflip get_memes failed: {data}")

    # Stick to classic top/bottom-text templates for v1.
    two_box_templates = [m for m in data["data"]["memes"] if m.get("box_count") == 2]
    return two_box_templates[:limit]


def caption_image(
    template_id: str, top_text: str, bottom_text: str, username: str, password: str
) -> str:
    response = requests.post(
        CAPTION_URL,
        data={
            "template_id": template_id,
            "username": username,
            "password": password,
            "text0": top_text,
            "text1": bottom_text,
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(f"imgflip caption_image failed: {data.get('error_message')}")
    return data["data"]["url"]
