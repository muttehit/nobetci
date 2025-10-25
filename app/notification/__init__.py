import requests


AD = requests.get(
    "https://raw.githubusercontent.com/kizil-aslan/nobetci-ads/refs/heads/main/main.txt").text
