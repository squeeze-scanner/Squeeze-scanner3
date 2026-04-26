import streamlit as st
import random

st.title("🎮 Guess the Number Game")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(1, 20)
    st.session_state.attempts = 0

guess = st.number_input("Guess a number (1–20)", 1, 20)

if st.button("Submit"):
    st.session_state.attempts += 1

    if guess < st.session_state.secret:
        st.write("⬆️ Too low")
    elif guess > st.session_state.secret:
        st.write("⬇️ Too high")
    else:
        st.success(f"🎉 Correct! It took you {st.session_state.attempts} tries")

if st.button("Restart"):
    st.session_state.secret = random.randint(1, 20)
    st.session_state.attempts = 0
    st.rerun()
