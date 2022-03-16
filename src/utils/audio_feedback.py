from playsound import playsound
import os

import pyttsx3
import gtts as gTTS




def main():
    # play_follow_me()
    # play_whatever_offline()
    # generate_or_play_audio(
    #     "commencing_search.mp3", "ALERT: commencing search for survivors."
    # )
    # generate_and_overwrite_audio(
    #     "exploration_complete.mp3",
    #     "ALERT: All frontiers have been exhausted, exploration is complete."
    # )
    generate_and_overwrite_audio(
        "guide_victim_out_of_view.mp3",
        "ALERT: The person I am guiding is no longer in view, going back!"
    )


def play_hi_follow_me():
    hi_follow_me = os.path.join("resource", "audio", "hi_follow_me.mp3")
    # playsound(hi_follow_me, False)
    playsound(hi_follow_me)


def generate_and_play_audio_offline(text="holla amigo, yo soy Pablo."):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def generate_or_play_audio(filename, text="holla amigo, yo soy Pablo."):
    path = os.path.join("resource", "audio", filename)

    if os.path.exists(path):
        playsound(path)
    else:
        generate_and_overwrite_audio(filename, text)


def generate_and_overwrite_audio(filename, text):
    path = os.path.join("resource", "audio", filename)

    tts = gTTS.gTTS(text=text, lang="en")
    tts.save(path)
    playsound(path)


def play_file(filename):
    path = os.path.join("resource", "audio", filename)
    playsound(path, False)


if __name__ == "__main__":
    main()
