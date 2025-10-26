#barkbarkbarkbarkbark

import obsws_python as obs
import os
import time

class Barker:
    _client = None
    _scene_name: str
    _source_name: str

    def connect(self):
        # Connect
        OBS_HOST = "localhost"
        OBS_PORT = 4455
        # Change the password here or in your obs websocket settings to match each other.
        OBS_PASS = "LaMn0A90jqbRifz3"

        self._client = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASS, timeout=3)

    def set_source(self, scene: str, source: str, audio_path: str):
        """
        Scene is the name of the scene in OBS that you want to spawn the source into.
        Source is what you want the source to be named. Audio_path is the path to the
        audio file.
        """
        self._scene_name = scene
        self._source_name = source

        if not self._client.get_scene_item_id(self._scene_name, self._source_name):
            self._client.create_input(
                sceneName=self._scene_name,
                inputName=self._source_name,
                inputKind="ffmpeg_source",
                inputSettings={
                    "local_file": audio_path,
                    "is_local_file": True,
                    "restart_on_activate": False,
                    "close_when_inactive": False
                },
                sceneItemEnabled=True
            )
            print(f"Created audio source: {self._source_name}")
        else:
            print("Audio source already exists!")

    def play(self):
        # Play/restart the media
        self._client.trigger_media_input_action(
            name=self._source_name,
            action="OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"
        )
        print("Playing audio...")

        # This is set to be about the length of the audio file
        time.sleep(3)

        # Get media duration and status
        status = self._client.get_media_input_status(name=self._source_name)
        print(f"Media state: {status.media_state}")
        print(f"Duration: {status.media_duration}ms")

    def disconnect(self):
        self._client.disconnect()

def main():
    barker = Barker()
    barker.connect()
    barker.set_source(scene="Robot", source="DogBark", audio_path=os.path.abspath("bark.mp3"))
    barker.play()
    barker.disconnect()

if __name__ == "__main__":
    main()