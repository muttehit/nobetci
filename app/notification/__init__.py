import requests

AD = requests.get(
    "https://raw.githubusercontent.com/kizil-aslan/nobetci-ads/refs/heads/main/main.txt").text


def reload_ad():
    global AD
    AD = requests.get(
        "https://raw.githubusercontent.com/kizil-aslan/nobetci-ads/refs/heads/main/main.txt").text


def get_ad():
    global AD
    return AD
