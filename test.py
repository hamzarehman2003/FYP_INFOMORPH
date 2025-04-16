import base64
import json
import requests
import time
import logging



def test_did_video_generation_with_mp3(local_audio_path: str):
    # Replace with your actual D-ID credentials in "username:password" format.
    did_credentials = "ZGV3YW5zdWxlbWFuQGdtYWlsLmNvbQ:hGb4v9vvf369YShpfQj5v"
    api_url = "https://api.d-id.com/talks"

    # Convert your D-ID credentials to a Base64-encoded string.
    encoded_credentials = base64.b64encode(did_credentials.encode()).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    # Upload the local MP3 file and obtain a publicly accessible URL.
    audio_url = "https://github.com/Syedhamza2/audio_hosting/raw/refs/heads/main/Recording.mp3"
    print(f"Obtained public audio URL: {audio_url}")

    # Create the payload using an audio script.
    payload = {
        "source_url": "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg",
        "script": {
            "type": "audio",
            "audio_url": audio_url
        }
    }
    
    # Create the talk (video request)
    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()  # raise exception if not successful

    data = response.json()
    print("Create talk response:")
    print(json.dumps(data, indent=4))
    
    # Extract the talk ID to poll for video status.
    talk_id = data.get("id")
    if not talk_id:
        print("No talk ID received. Check your API key and payload.")
        return

    # Poll for the video until it is ready.
    poll_url = f"{api_url}/{talk_id}"
    print("Polling for video status...")
    for i in range(15):  # Poll up to 15 times (adjust as needed)
        poll_response = requests.get(poll_url, headers=headers)
        poll_response.raise_for_status()
        poll_data = poll_response.json()
        
        status = poll_data.get("status")
        print(f"Poll {i+1}: status = {status}")
        
        if status == "done":
            video_url = poll_data.get("result_url")
            print("Video is ready!")
            print("Video URL:", video_url)
            return
        elif status == "failed":
            print("Video generation failed.")
            return
        time.sleep(2)  # Wait 2 seconds between polls

    print("Timed out waiting for video generation.")

if __name__ == "__main__":
    try:
        # Provide the path to your local MP3 file.
        test_did_video_generation_with_mp3("path/to/your_audio_file.mp3")
    except Exception as e:
        print("Test failed:", e)