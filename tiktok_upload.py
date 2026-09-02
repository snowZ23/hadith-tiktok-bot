import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error


TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
UPLOAD_URL = "https://open.tiktokapis.com/v2/post/publish/content/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"


def request(url, data, headers):
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body}")


client_key = os.environ["TIKTOK_CLIENT_KEY"]
client_secret = os.environ["TIKTOK_CLIENT_SECRET"]
refresh_token = os.environ["TIKTOK_REFRESH_TOKEN"]
photo_url = os.environ["TIKTOK_PHOTO_URL"]
refresh_out = os.environ.get(
    "TIKTOK_REFRESH_OUT",
    "/tmp/tiktok_new_refresh_token"
)


# -------------------------------------------------
# 1. Refresh Access Token
# -------------------------------------------------

token_data = urllib.parse.urlencode({
    "client_key": client_key,
    "client_secret": client_secret,
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
}).encode("utf-8")

tokens = request(
    TOKEN_URL,
    token_data,
    {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
)

access_token = tokens.get("access_token")

if not access_token:
    print("TikTok token refresh failed.")
    print(json.dumps(tokens, ensure_ascii=False))
    sys.exit(1)

new_refresh_token = tokens.get(
    "refresh_token",
    refresh_token
)

# لا نطبع التوكنات في Logs
with open(refresh_out, "w", encoding="utf-8") as f:
    f.write(new_refresh_token)

print("TikTok access token refreshed successfully.")


# -------------------------------------------------
# 2. Upload Hadith photo
# -------------------------------------------------

upload_body = {
    "post_info": {
        "title": "حديث اليوم",
        "description": "حديث اليوم"
    },
    "source_info": {
        "source": "PULL_FROM_URL",
        "photo_cover_index": 0,
        "photo_images": [
            photo_url
        ]
    },
    "post_mode": "MEDIA_UPLOAD",
    "media_type": "PHOTO"
}

upload_response = request(
    UPLOAD_URL,
    json.dumps(
        upload_body,
        ensure_ascii=False
    ).encode("utf-8"),
    {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
)

error = upload_response.get("error", {})

if error.get("code") != "ok":
    print("TikTok upload failed:")
    print(json.dumps(upload_response, ensure_ascii=False))
    sys.exit(1)

publish_id = upload_response.get("data", {}).get("publish_id")

if not publish_id:
    print("TikTok did not return publish_id.")
    sys.exit(1)

print("TikTok accepted Hadith.")
print("Publish ID:", publish_id)


# -------------------------------------------------
# 3. Check processing status
# -------------------------------------------------

for attempt in range(18):

    time.sleep(5)

    status_response = request(
        STATUS_URL,
        json.dumps({
            "publish_id": publish_id
        }).encode("utf-8"),
        {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
    )

    status_error = status_response.get("error", {})

    if status_error.get("code") != "ok":
        print("Could not check TikTok status.")
        print(json.dumps(status_response, ensure_ascii=False))
        sys.exit(1)

    data = status_response.get("data", {})
    status = data.get("status", "UNKNOWN")

    print("TikTok status:", status)

    if status == "FAILED":
        print(
            "Fail reason:",
            data.get("fail_reason", "unknown")
        )
        sys.exit(1)

    if status in (
        "SEND_TO_USER_INBOX",
        "PUBLISH_COMPLETE"
    ):
        print("Hadith successfully sent to TikTok Inbox.")
        sys.exit(0)


print("TikTok is still processing the upload.")
