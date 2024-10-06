import streamlit as st
import requests
import json
import time
import random

# Extended emoji dictionary for local fallback
emoji_dict = {
    "happy": ["😊", "😃", "😄", "😁"],
    "sad": ["😢", "😭", "😞", "☹️"],
    "love": ["❤️", "😍", "🥰", "💖"],
    "angry": ["😠", "😡", "🤬", "💢"],
    "surprised": ["😮", "😲", "😯", "🤯"],
    "sana": ["💖", "🥰"],
    "taufik": ["😎","❤️ u too"],
    # Add more mappings here
}

def local_text_to_emoji(text):
    text = text.lower()
    for key, emojis in emoji_dict.items():
        if key in text:
            return random.choice(emojis)
    return None

def text_to_emoji(text):
    # First, try local conversion
    local_emoji = local_text_to_emoji(text)
    if local_emoji:
        return local_emoji
    
    # If local conversion fails, use the Hugging Face API
    api_key = st.secrets["huggingface_api_key"]
    url = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "inputs": text
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Map the emotion to an emoji
            emotion_to_emoji = {
                "joy": "😄",
                "sadness": "😢",
                "anger": "😠",
                "fear": "😨",
                "surprise": "😮",
                "love": "❤️",
                "neutral": "😐"
            }
            
            # Get the emotion with the highest score
            top_emotion = max(result[0], key=lambda x: x['score'])['label']
            return emotion_to_emoji.get(top_emotion, "❓")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if attempt < max_retries - 1:
                    st.warning(f"Rate limit exceeded. Retrying in {2**attempt} seconds...")
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    st.warning("API unavailable. Using local conversion.")
                    return local_text_to_emoji(text) or "❓"
            else:
                st.error(f"HTTP error occurred: {e}")
                return local_text_to_emoji(text) or "❓"
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return local_text_to_emoji(text) or "❓"

# Streamlit app
st.title("Text to Emoji")

# Input text
input_text = st.text_input("Enter text to convert to emoji:")

if st.button("Convert"):
    if input_text:
        with st.spinner("Converting..."):
            emoji = text_to_emoji(input_text)
        if emoji:
            st.success(f"{emoji}")
        else:
            st.warning("Couldn't convert to emoji. Try a different text.")
    else:
        st.warning("Please enter some text to convert.")
