import base64
import requests

AD = base64.b64decode(requests.get(
        f"https://api.github.com/repos/kizil-aslan/nobetci-ads/contents/main.txt", headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }).json()["content"]).decode("utf-8")


def reload_ad():
    global AD
    AD = base64.b64decode(requests.get(
        f"https://api.github.com/repos/kizil-aslan/nobetci-ads/contents/main.txt", headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }).json()["content"]).decode("utf-8")


def get_ad():
    global AD
    return AD
