import pygame


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


if __name__ == '__main__':
    print("Testing `audio_handler`")
    initialize_audio()
    set_volume(1)
    play_sound("../../assets/sounds/bad-to-the-bone.mp3")
    input("Press Enter to stop the sound...")
    stop_sound()
    print("Done")
