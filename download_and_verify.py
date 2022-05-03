#!/usr/bin/env python3
import requests # you need to run pip3 install requests (or install from apt)
import json
import os
import hashlib
import sys

if len(sys.argv) < 3:
    print(f"Usage: python3 {sys.argv[0]} /path/to/profile/directory client|server")
    exit(1)

profile_dir = sys.argv[1]
download_mode = sys.argv[2]

is_client = download_mode == "client"
is_server = download_mode == "server"
if not is_client and not is_server:
    print("mode should be client or server")
mc_version = "1.18.2"

tools_dir = os.path.dirname(__file__)
downloads_json = json.load(open(tools_dir + "/downloads.json", "r"))
print("Downloading Mods...")

for file in downloads_json["files"]:
    if "mods/SERVER" in file["path"]:
        if is_server:
            file["path"] = file["path"].replace("mods/SERVER", "mods/" + mc_version)
        else:
            continue
    print("Downloading", file["path"], "from", file["url"])
    localpath = profile_dir + "/" + file["path"]
    r = requests.get(file["url"])
    r.raise_for_status()
    print("Downloaded!")
    # check downloaded files checksum
    rhash = hashlib.sha256(r.content).hexdigest()
    print("SHA-256 Checksum", rhash)
    if file["sha256"] == "SKIP":
        print("Skip SHA-256 Check due to marked as SKIP")
    else:
        if file["sha256"] == rhash:
            print("SHA-256 Check: Passed")
        else:
            print("SHA-256 is WRONG!!")
            print("expected:", file["sha256"])
            print("actually:", rhash)
            print("exiting...")
            exit(1)
    os.makedirs(os.path.dirname(localpath), exist_ok=True)
    if os.path.exists(localpath):
        # check checksum
        print("Local file exists")
        with open(localpath, "rb") as f:
            localhash = hashlib.sha256(f.read()).hexdigest()
        if localhash == rhash:
            print("Local file is up-to-date")
            continue
        print("local file checksum is wrong")
        print("local:", localhash)
        print("remote:", rhash)
    else:
        print("Saving as", file["path"])
        with open(localpath, "wb") as f:
            f.write(r.content)