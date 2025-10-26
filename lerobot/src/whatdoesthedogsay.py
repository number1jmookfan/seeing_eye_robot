#barkbarkbarkbarkbark

import obsws_python as obs
import os
import time

def main():
    audio_file_path = os.path.abspath("bark.mp3")
    # Connect
    OBS_HOST = "localhost"
    OBS_PORT = 4455
    # Change the password here or in your obs websocket settings to match each other.
    OBS_PASS = "LaMn0A90jqbRifz3"
    client = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASS, timeout=3)

    try:
        # Method 1: Create a new media source with audio file
        scene_name = "Robot"  # Your scene name
        source_name = "DogBark"

        # Create media source
        if not client.get_scene_item_id(scene_name, source_name):
            client.create_input(
                sceneName=scene_name,
                inputName=source_name,
                inputKind="ffmpeg_source",
                inputSettings={
                    "local_file": audio_file_path,
                    "is_local_file": True,
                    "restart_on_activate": True,
                    "close_when_inactive": False
                },
                sceneItemEnabled=True
            )
        print(f"Created audio source: {source_name}")

        # Method 2: Control existing media source
        # Play/restart the media
        client.trigger_media_input_action(
            name=source_name,
            action="OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"
        )
        print("Playing audio...")

        # This is set to be about the length of the audio file
        time.sleep(3)

        # Get media duration and status
        status = client.get_media_input_status(name=source_name)
        print(f"Media state: {status.media_state}")
        print(f"Duration: {status.media_duration}ms")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()