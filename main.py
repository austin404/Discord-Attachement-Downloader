#!/usr/bin/env python3
"""
Discord: attachment downloader
@author: austin404
"""

from typing import Union
import requests
import json
from os import path
import os

# Don't change this if you are okay with names like 0.jpeg, 1.jpeg .....
NAME = 0  # This is counter for naming files like 0.jpeg, 1.jpeg
TOTAL_RESULTS = 0  # To calculate if it exceeds max result
###

# Required
DIRECTORY = "data"  # Directory where you want to save
# Your token comes here
TOKEN = ""
MAX_RESULT_LIMIT = 200  # Would be nice if its a multiple of 100
CHANNEL_ID = ""  # You channel ID comes here
###


MESSAGE_END = ""  # If you want to end at a particular message
HEADERS = {
    "Authorization": TOKEN
}


def download(url: str) -> None:
    global NAME
    r = requests.get(url=url)

    _path = path.join(DIRECTORY, str(NAME))
    extension = url.split('/')[-1].split('.')[-1]
    filename = f"{_path}.{extension}"

    with open(filename, 'wb') as f:
        f.write(r.content)
    r.close()
    NAME += 1


def get_data(url: str, before: Union[str, None], limit: int) -> None:
    global TOTAL_RESULTS

    if TOTAL_RESULTS > MAX_RESULT_LIMIT:
        return

    request_url = ""

    if before:
        request_url = url + f"?before={before}&limit={limit}"
    else:
        request_url = url + f"?limit={limit}"

    TOTAL_RESULTS += limit

    r = requests.get(url=request_url, headers=HEADERS)
    if r.status_code != 200:
        print(r.text)
        return

    name = f"{TOTAL_RESULTS - limit} to {TOTAL_RESULTS}"

    print(
        f"status code = {r.status_code} for limit {name}")
    data = r.json()
    with open(f'result {name}.json', 'w') as f:
        json.dump(data, f, indent=2)

    for i in data:
        if MESSAGE_END and i["content"] == MESSAGE_END:
            r.close()
            return
        for attachment in i["attachments"]:
            download_url = attachment['url']
            with open('urls.txt', 'a') as f:
                f.write(f"{download_url}\n")
            download(download_url)
    r.close()
    get_data(url=url, before=data[-1]["id"], limit=100)


# Nothing here just to make sure nothing weird happens in log files
try:
    os.remove('urls.txt')
except:
    pass
try:
    os.mkdir(DIRECTORY)
except:
    pass

url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"

get_data(url=url, before=None, limit=100)
