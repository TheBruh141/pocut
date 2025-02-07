import pygame
import threading
import time


def initialize_audio():
    """
    Initialize pygame's mixer for audio playback.
    """
    try:
        pygame.mixer.init()
        print("Audio initialized successfully.")
    except pygame.error as e:
        print(f"Error initializing audio: {e}")


def play_sound(file_path: str):
    """
    Play a sound file.
    @param file_path Path to the audio file.
    """
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        print(f"Playing sound: {file_path}")
    except pygame.error as e:
        print(f"Error playing sound: {e}")


def play_sound_blocking(file_path: str):
    """
    Play a sound file and block until it finishes.
    @param file_path Path to the audio file.
    """
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # Wait for the music to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def play_sound_time(
    file_path: str, max_time: float, fade_out: bool = False, fade_duration: float = 2.0
):
    """
    Play a sound file for a specified duration without blocking the main thread.

    @param file_path: Path to the audio file.
    @param max_time: Maximum playback time in seconds.
    @param fade_out: If True, the music will fade out before stopping.
    @param fade_duration: Duration of the fade-out effect in seconds.
    """
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    def stop_music_after_delay():
        time.sleep(max_time - fade_duration if fade_out else max_time)

        if fade_out:
            pygame.mixer.music.fadeout(int(fade_duration * 1000))
            time.sleep(fade_duration)  # Allow fade-out to complete

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        print(f"Music stopped after {max_time} seconds with fade-out={fade_out}")

    # Start the timer in a separate thread
    timer_thread = threading.Thread(target=stop_music_after_delay)
    timer_thread.start()


def set_volume(level: float):
    """
    Set the volume for audio playback.
    @param level Volume level between 0.0 and 1.0.
    """
    pygame.mixer.music.set_volume(level)


def stop_sound():
    """
    Stop any currently playing sound.
    """
    pygame.mixer.music.stop()


if __name__ == "__main__":
    print("Testing `audio_handler`")
    initialize_audio()
    set_volume(1)
    # play_sound("../../assets/sounds/bad-to-the-bone.mp3")
    # input("Press Enter to stop the sound...")
    # stop_sound()
    # print("Done")

    # Run the function and perform other operations
    play_sound_time("../../assets/sounds/Mice_on_venus.mp3", 10, True, fade_duration=5)

    # Simulating main thread activity
    for i in range(10):
        print(f"Main thread running: {i}")
        time.sleep(1)

    print("Main thread finished execution.")
