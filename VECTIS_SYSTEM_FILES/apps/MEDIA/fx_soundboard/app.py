import streamlit as st

st.set_page_config(page_title="FX Soundboard", page_icon="🔊")
st.title("🔊 FX Soundboard")

sounds = {
    "Applause 👏": "https://www.soundjay.com/human/applause-01.mp3",
    "Drum Roll 🥁": "https://www.soundjay.com/misc/sounds/drum-roll-01.mp3",
    "Success Chime ✨": "https://www.soundjay.com/misc/sounds/magic-chime-01.mp3",
    "Fail Trombone 📉": "https://www.soundjay.com/human/sounds/fail-trombone-01.mp3",
    "Rimshot 🤣": "https://www.soundjay.com/misc/sounds/rimshot-01.mp3"
}

cols = st.columns(3)
for i, (name, url) in enumerate(sounds.items()):
    with cols[i % 3]:
        st.write(f"**{name}**")
        st.audio(url)

st.divider()
st.write("Sounds from SoundJay.com (Free)")
