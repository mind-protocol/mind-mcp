"""
Twitter/X Bridge — Post tweets via OAuth 1.0a + API v2.

Used by mcp/tools/send_handler.py via:
    from twitter_bridge import post_tweet
"""

import os
import json
import hashlib
import hmac
import time
import urllib.parse
import urllib.request
import logging
from typing import Optional

logger = logging.getLogger("mind.twitter_bridge")

# OAuth 1.0a credentials
CONSUMER_KEY = os.environ.get("X_CONSUMER_KEY", "")
CONSUMER_SECRET = os.environ.get("X_CONSUMER_SECRET", "")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
ACCESS_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET", "")


def _oauth_sign(method: str, url: str, params: dict) -> str:
    """Generate OAuth 1.0a signature."""
    # Collect all params (oauth + request)
    all_params = dict(params)

    # Sort and encode
    sorted_params = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
        for k, v in sorted(all_params.items())
    )

    # Signature base string
    base = "&".join([
        method.upper(),
        urllib.parse.quote(url, safe=""),
        urllib.parse.quote(sorted_params, safe=""),
    ])

    # Signing key
    signing_key = f"{urllib.parse.quote(CONSUMER_SECRET, safe='')}&{urllib.parse.quote(ACCESS_SECRET, safe='')}"

    # HMAC-SHA1
    import base64
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    ).decode()

    return sig


def _oauth_header(method: str, url: str) -> str:
    """Build the OAuth Authorization header."""
    import uuid

    oauth_params = {
        "oauth_consumer_key": CONSUMER_KEY,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": ACCESS_TOKEN,
        "oauth_version": "1.0",
    }

    sig = _oauth_sign(method, url, oauth_params)
    oauth_params["oauth_signature"] = sig

    header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
    )
    return header


def post_tweet(text: str, reply_to: Optional[str] = None) -> Optional[dict]:
    """Post a tweet via X API v2.

    Args:
        text: Tweet text (max 280 chars)
        reply_to: Optional tweet ID to reply to

    Returns:
        API response dict or None on failure
    """
    if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        logger.error("X API credentials not set (X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)")
        return None

    url = "https://api.twitter.com/2/tweets"

    payload = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}

    body = json.dumps(payload).encode()

    auth_header = _oauth_header("POST", url)

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            tweet_id = result.get("data", {}).get("id", "?")
            logger.info(f"Tweet posted: {tweet_id} ({len(text)} chars)")
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        logger.error(f"X API error {e.code}: {error_body[:200]}")
        return None
    except Exception as e:
        logger.error(f"Tweet post failed: {e}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = post_tweet(text)
        if result:
            print(f"Posted: {result}")
        else:
            print("Failed")
    else:
        print("Usage: python3 twitter_bridge.py <tweet text>")
