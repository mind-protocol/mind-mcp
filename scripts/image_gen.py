#!/usr/bin/env python3
"""Image generation for MIND — Gemini (primary) + Ideogram (fallback).

Usage:
    python3 scripts/image_gen.py "A serene Japanese garden at sunset"
    python3 scripts/image_gen.py --backend gemini "Portrait of a wise owl"
    python3 scripts/image_gen.py --backend ideogram --style REALISTIC "Cyberpunk city"
    python3 scripts/image_gen.py --aspect 16:9 --resolution 2K "4K landscape"
"""

import json
import os
import sys
import time
import base64
import requests
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STATE_DIR = PROJECT_ROOT / "shrine" / "state"
IMAGE_DIR = STATE_DIR / "images"

# Track CDN URLs for generated images (path → URL mapping)
# Used by WAHA CORE which can't send files — sends URL as text instead
_image_cdn_urls: dict[str, str] = {}


def get_image_url(path) -> str | None:
    """Get a public URL for a generated image.
    Priority: CDN URL (Ideogram) → self-hosted /generated/<filename> URL.
    """
    cdn = _image_cdn_urls.get(str(path))
    if cdn:
        return cdn
    # Fallback: construct URL from MIND_PUBLIC_URL + /generated/<filename>
    public_url = os.environ.get("MIND_PUBLIC_URL", "")
    if public_url:
        filename = Path(path).name
        return f"{public_url}/generated/{filename}"
    return None

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env", override=True)
except ImportError:
    pass

# API config
IDEOGRAM_API_URL = "https://api.ideogram.ai/v1/ideogram-v3/generate"
IDEOGRAM_API_KEY = os.environ.get("IDEOGRAM_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Defaults
DEFAULT_STYLE = "AUTO"
DEFAULT_ASPECT = "1x1"
DEFAULT_SPEED = "TURBO"

# Valid options
VALID_STYLES = {"AUTO", "GENERAL", "REALISTIC", "DESIGN", "FICTION"}
VALID_ASPECTS = {
    "1x1", "16x9", "9x16", "4x3", "3x4", "3x2", "2x3",
    "16x10", "10x16", "3x1", "1x3"
}
VALID_SPEEDS = {"FLASH", "TURBO", "DEFAULT", "QUALITY"}


def _gemini_aspect_to_ideogram(aspect: str) -> str:
    """Convert Gemini aspect format (16:9) to Ideogram format (16x9)."""
    return aspect.replace(":", "x")


def _ideogram_aspect_to_gemini(aspect: str) -> str:
    """Convert Ideogram aspect format (16x9) to Gemini format (16:9)."""
    return aspect.replace("x", ":")


GEMINI_VALID_ASPECTS = {"1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"}
GEMINI_VALID_RESOLUTIONS = {"1K", "2K", "4K"}


def generate_image_gemini(
    prompt: str,
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    model: str = "gemini-3-pro-image-preview",
) -> list[Path]:
    """Generate image via Gemini API (google-genai SDK).

    Returns list of saved image paths, or empty list on failure.
    """
    if not GEMINI_API_KEY:
        print("  ✗ GEMINI_API_KEY not set in .env")
        return []

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("  ✗ google-genai not installed (pip install google-genai)")
        return []

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Normalize aspect ratio
    if "x" in aspect_ratio:
        aspect_ratio = _ideogram_aspect_to_gemini(aspect_ratio)
    if aspect_ratio not in GEMINI_VALID_ASPECTS:
        aspect_ratio = "1:1"
    if resolution not in GEMINI_VALID_RESOLUTIONS:
        resolution = "1K"

    try:
        label = f"\"{prompt[:60]}...\"" if len(prompt) > 60 else f"\"{prompt}\""
        print(f"  🎨 Gemini generating: {label}")
        t0 = time.time()

        client = genai.Client(api_key=GEMINI_API_KEY)

        config_kwargs = {
            "response_modalities": ['IMAGE'],
        }
        # Only set image_size for pro model
        if "pro" in model:
            config_kwargs["image_config"] = types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution,
            )
        else:
            config_kwargs["image_config"] = types.ImageConfig(
                aspect_ratio=aspect_ratio,
            )

        response = client.models.generate_content(
            model=model,
            contents=[prompt],
            config=types.GenerateContentConfig(**config_kwargs),
        )

        elapsed = time.time() - t0

        saved = []
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        for i, part in enumerate(response.parts):
            if part.inline_data is not None:
                img_data = part.inline_data.data
                if isinstance(img_data, str):
                    img_data = base64.b64decode(img_data)

                suffix = f"_{i}" if len([p for p in response.parts if p.inline_data]) > 1 else ""
                filename = f"gemini_{ts}{suffix}.png"
                path = IMAGE_DIR / filename
                path.write_bytes(img_data)
                saved.append(path)
                print(f"  ✓ Saved: {path.name} ({len(img_data) // 1024}KB, {elapsed:.1f}s)")
            elif part.text is not None:
                print(f"  ℹ Gemini text: {part.text[:100]}")

        if not saved:
            print("  ✗ Gemini returned no images")

        return saved

    except Exception as e:
        err = str(e)
        if "SAFETY" in err.upper() or "BLOCKED" in err.upper():
            print(f"  ✗ Gemini: prompt blocked by safety filter")
        elif "429" in err or "RATE" in err.upper():
            print(f"  ✗ Gemini: rate limited")
        else:
            print(f"  ✗ Gemini error: {err[:200]}")
        return []


def generate_image_ideogram(
    prompt: str,
    style_type: str = DEFAULT_STYLE,
    aspect_ratio: str = DEFAULT_ASPECT,
    rendering_speed: str = DEFAULT_SPEED,
    negative_prompt: str = "",
    num_images: int = 1,
    seed: int = None,
) -> list[Path]:
    """Generate image(s) via Ideogram API.

    Returns list of saved image paths, or empty list on failure.
    """
    if not IDEOGRAM_API_KEY:
        print("  ✗ IDEOGRAM_API_KEY not set in .env")
        return []

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Validate params
    style_type = style_type.upper() if style_type.upper() in VALID_STYLES else DEFAULT_STYLE
    aspect_ratio = aspect_ratio if aspect_ratio in VALID_ASPECTS else DEFAULT_ASPECT
    rendering_speed = rendering_speed.upper() if rendering_speed.upper() in VALID_SPEEDS else DEFAULT_SPEED

    # Build request
    payload = {
        "prompt": prompt,
        "style_type": style_type,
        "aspect_ratio": aspect_ratio,
        "rendering_speed": rendering_speed,
        "num_images": num_images,
        "magic_prompt": "AUTO",
    }
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if seed is not None:
        payload["seed"] = seed

    headers = {
        "Api-Key": IDEOGRAM_API_KEY,
    }

    try:
        label = f"\"{prompt[:60]}...\"" if len(prompt) > 60 else f"\"{prompt}\""
        print(f"  🎨 Ideogram generating: {label}")
        t0 = time.time()

        resp = requests.post(
            IDEOGRAM_API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )

        elapsed = time.time() - t0

        if resp.status_code == 402:
            print("  ✗ Ideogram: insufficient balance — add credits at ideogram.ai")
            return []
        if resp.status_code == 422:
            print("  ✗ Ideogram: prompt blocked by safety filter")
            return []
        if resp.status_code == 429:
            print("  ✗ Ideogram: rate limited — try again in a moment")
            return []
        if not resp.ok:
            print(f"  ✗ Ideogram API error {resp.status_code}: {resp.text[:200]}")
            return []

        result = resp.json()
        images = result.get("data", [])
        if not images:
            print("  ✗ No images returned")
            return []

        # Download and save images
        saved = []
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        for i, img in enumerate(images):
            url = img.get("url")
            if not url:
                continue

            img_resp = requests.get(url, timeout=60)
            if not img_resp.ok:
                print(f"  ✗ Failed to download image {i}: {img_resp.status_code}")
                continue

            suffix = f"_{i}" if num_images > 1 else ""
            filename = f"ideogram_{ts}{suffix}.png"
            path = IMAGE_DIR / filename
            path.write_bytes(img_resp.content)
            saved.append(path)
            _image_cdn_urls[str(path)] = url  # Store CDN URL for WAHA CORE fallback
            print(f"  ✓ Saved: {path.name} ({len(img_resp.content) // 1024}KB, {elapsed:.1f}s)")

        return saved

    except requests.Timeout:
        print("  ✗ Ideogram API timeout (120s)")
        return []
    except Exception as e:
        print(f"  ✗ Ideogram error: {e}")
        return []


def generate_image(
    prompt: str,
    style_type: str = DEFAULT_STYLE,
    aspect_ratio: str = DEFAULT_ASPECT,
    rendering_speed: str = DEFAULT_SPEED,
    negative_prompt: str = "",
    num_images: int = 1,
    seed: int = None,
    backend: str = "auto",
    resolution: str = "1K",
) -> list[Path]:
    """Generate image with fallback chain: Gemini → Ideogram.

    backend: 'auto' (try gemini first), 'gemini', or 'ideogram'
    """
    # Normalize aspect for cross-backend compat
    gemini_aspect = _ideogram_aspect_to_gemini(aspect_ratio) if "x" in aspect_ratio else aspect_ratio
    ideogram_aspect = _gemini_aspect_to_ideogram(aspect_ratio) if ":" in aspect_ratio else aspect_ratio

    if backend in ("auto", "gemini"):
        result = generate_image_gemini(
            prompt=prompt,
            aspect_ratio=gemini_aspect,
            resolution=resolution,
        )
        if result:
            return result
        if backend == "gemini":
            return []
        print("  ↳ Falling back to Ideogram...")

    return generate_image_ideogram(
        prompt=prompt,
        style_type=style_type,
        aspect_ratio=ideogram_aspect,
        rendering_speed=rendering_speed,
        negative_prompt=negative_prompt,
        num_images=num_images,
        seed=seed,
    )


def parse_image_tag(text: str) -> tuple[str, str]:
    """Extract [GENERATE_IMAGE: prompt] tag from response text.

    Returns (clean_text, image_prompt) or (text, None) if no tag found.
    """
    import re
    match = re.search(r'\[GENERATE_IMAGE:\s*(.+?)\]', text, re.DOTALL)
    if match:
        image_prompt = match.group(1).strip()
        clean_text = text[:match.start()] + text[match.end():]
        clean_text = clean_text.strip()
        return clean_text, image_prompt
    return text, None


def parse_imagine_command(text: str) -> dict | None:
    """Parse /imagine command from Telegram message.

    Supports:
        /imagine A sunset over mountains
        /imagine --style realistic --aspect 16x9 A sunset over mountains
        /image A cat on a roof
        /img --speed quality A neon city

    Returns dict with prompt + optional kwargs, or None if not an imagine command.
    """
    import re
    text = text.strip()
    # Check for command prefix
    match = re.match(r'^/(imagine|image|img)\b\s*', text, re.IGNORECASE)
    if not match:
        return None

    rest = text[match.end():].strip()
    if not rest:
        return None

    # Parse optional flags
    result = {"prompt": None, "style_type": None, "aspect_ratio": None, "rendering_speed": None, "negative_prompt": None}
    parts = []
    tokens = rest.split()
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.startswith("--") and i + 1 < len(tokens):
            flag = t[2:].lower()
            val = tokens[i + 1]
            if flag == "style" and val.upper() in VALID_STYLES:
                result["style_type"] = val.upper()
                i += 2
                continue
            elif flag == "aspect" and val in VALID_ASPECTS:
                result["aspect_ratio"] = val
                i += 2
                continue
            elif flag == "speed" and val.upper() in VALID_SPEEDS:
                result["rendering_speed"] = val.upper()
                i += 2
                continue
            elif flag in ("negative", "neg"):
                result["negative_prompt"] = val
                i += 2
                continue
        parts.append(t)
        i += 1

    prompt = " ".join(parts).strip()
    if not prompt:
        return None
    result["prompt"] = prompt
    return result


# CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate images (Gemini + Ideogram)")
    parser.add_argument("prompt", help="Image description")
    parser.add_argument("--backend", default="auto", choices=["auto", "gemini", "ideogram"])
    parser.add_argument("--style", default=DEFAULT_STYLE, choices=sorted(VALID_STYLES))
    parser.add_argument("--aspect", default="1:1", help="Aspect ratio (e.g. 16:9 or 16x9)")
    parser.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"], help="Gemini resolution")
    parser.add_argument("--speed", default=DEFAULT_SPEED, choices=sorted(VALID_SPEEDS))
    parser.add_argument("--negative", default="", help="Negative prompt (Ideogram only)")
    parser.add_argument("--count", type=int, default=1, help="Number of images (Ideogram only)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (Ideogram only)")
    args = parser.parse_args()

    paths = generate_image(
        prompt=args.prompt,
        backend=args.backend,
        style_type=args.style,
        aspect_ratio=args.aspect,
        resolution=args.resolution,
        rendering_speed=args.speed,
        negative_prompt=args.negative,
        num_images=args.count,
        seed=args.seed,
    )

    if paths:
        print(f"\nGenerated {len(paths)} image(s):")
        for p in paths:
            print(f"  {p}")
    else:
        print("\nFailed to generate image.")
        sys.exit(1)
