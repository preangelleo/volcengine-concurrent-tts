import asyncio
import os
import base64
import uuid
import aiohttp

async def generate_audio_async(session: aiohttp.ClientSession, app_id: str, access_key: str, text: str, voice_type: str = "BV001_streaming") -> bytes:
    """
    Asynchronously calls the Volcano Engine TTS API to generate audio via HTTP POST.

    :param session: An aiohttp.ClientSession instance.
    :param app_id: Your Volcano Engine App ID.
    :param access_key: Your Volcano Engine Access Key (used as Bearer token for authentication).
    :param text: The text to be synthesized.
    :param voice_type: The desired official voice for synthesis.
    :return: The audio content in bytes.
    :raises Exception: If the API call fails or returns an error.
    """

    # Use standard voice cluster for all official voices
    cluster = "volcano_tts"

    url = "https://openspeech.bytedance.com/api/v1/tts"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer;{access_key}" # Using access_key as the token as per documentation
    }

    body = {
        "app": {
            "appid": app_id,
            "token": access_key, # Using access_key as token for volcano_tts cluster
            "cluster": cluster
        },
        "user": {
            "uid": str(uuid.uuid4()) # Arbitrary unique user ID
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()), # Unique request ID
            "text": text,
            "text_type": "plain",
            "operation": "query" # For HTTP non-streaming API
        }
    }

    try:
        async with session.post(url, headers=headers, json=body) as response:
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            res_json = await response.json()

            if res_json.get("code") == 3000 and "data" in res_json:
                # The API returns base64 encoded audio data
                return base64.b64decode(res_json["data"])
            else:
                error_message = res_json.get("message", "Unknown API error")
                raise Exception(f"Volcano Engine TTS API error: {error_message} (Code: {res_json.get('code')})")
    except aiohttp.ClientError as e:
        raise Exception(f"Network or HTTP client error: {e}")
    except Exception as e:
        raise Exception(f"Error during TTS API call: {e}")
