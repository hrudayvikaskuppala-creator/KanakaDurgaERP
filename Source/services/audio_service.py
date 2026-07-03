"""
===========================================
 Audio Service
===========================================
Single place that owns background music playback for the whole app
(loading screen + dashboard), so there's one source of truth for
"is audio on or off right now" instead of every screen managing its
own pygame state.

Because pygame's mixer is process-global, music started on the
loading screen keeps playing seamlessly once the dashboard opens -
there's no need to stop and restart it, which is what makes the
"plays smoothly throughout the application" behavior work.
"""

import os

from services.campany_service import get_audio_muted, set_audio_muted

SPLASH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "splash"
)
AUDIO_CANDIDATES = ["splash_audio.mp3", "splash_audio.wav"]

BACKGROUND_VOLUME = 0.7  # comfortable "background", not a full-volume song

_state = {
    "initialized": False,
    "muted": None,      # loaded lazily from Settings on first use
    "available": False, # False if pygame/audio device isn't usable
}


def _find_audio_file():
    for name in AUDIO_CANDIDATES:
        path = os.path.join(SPLASH_DIR, name)
        if os.path.isfile(path):
            return path
    return None


def _ensure_mixer():
    if _state["initialized"]:
        return _state["available"]

    _state["initialized"] = True

    try:
        import pygame
        pygame.mixer.init()
        _state["available"] = True
        print("✅ Pygame initialized successfully")
    except Exception as e:
        print("❌ Audio Error:", e)
        _state["available"] = False

    return _state["available"]


def is_muted():
    if _state["muted"] is None:
        _state["muted"] = get_audio_muted()
    return _state["muted"]


def play_background_music(loop=True):
    """
    Starts the devotional track. Safe to call multiple times - if
    it's already playing, this is a no-op rather than restarting it
    (avoids an audible restart/click when navigating between the
    loading screen and dashboard).
    """
    if not _ensure_mixer():
        return

    import pygame

    if pygame.mixer.music.get_busy():
        return  # already playing - don't restart it

    audio_path = _find_audio_file()
    if not audio_path:
        return

    try:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.set_volume(0 if is_muted() else BACKGROUND_VOLUME)
        pygame.mixer.music.play(loops=-1 if loop else 0)
    except Exception:
        pass


def set_muted(muted):
    """
    Mutes/unmutes instantly (fades the current track's volume rather
    than stopping it, so unmuting resumes right where the music was)
    and remembers the choice for next time the app opens.
    """
    _state["muted"] = muted
    set_audio_muted(muted)

    if _ensure_mixer():
        import pygame
        try:
            pygame.mixer.music.set_volume(0 if muted else BACKGROUND_VOLUME)
            # If nothing is loaded/playing yet (e.g. user unmutes after
            # muting before any track ever started), start it now.
            if not muted and not pygame.mixer.music.get_busy():
                play_background_music()
        except Exception:
            pass


def toggle_mute():
    set_muted(not is_muted())
    return _state["muted"]
