import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
from gtts import gTTS 
import pygame 
import os
import datetime
import webbrowser
import requests
import threading
import google.generativeai as genai
import time


GEMINI_API_KEY = ""

class SmartAssistant:
    def __init__(self):
        self.llm_active = False
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            
            self.llm_active = True
            print(" AI System Connected")
        except Exception as e:
            print(f" API Key Error: {e}")

    def speak(self, text):
        try:
            print(f" Assistant: {text}")
          
            tts = gTTS(text=text, lang='en', slow=False)
            filename = "voice_response.mp3"
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    filename = f"voice_{int(time.time())}.mp3"
            
            tts.save(filename)
          
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
    
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.quit()
            try:
                os.remove(filename)
            except:
                pass
                
        except Exception as e:
            print(f"Audio Error: {e}")

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                command = recognizer.recognize_google(audio, language="en-US")
                return command.lower()
            except:
                return None

    def process_logic(self, command):
        if "open youtube" in command:
            webbrowser.open("https://youtube.com")
            return "Opening YouTube."
        elif "time" in command:
            return f"It is {datetime.datetime.now().strftime('%I:%M %p')}"
        elif "google" in command:
            webbrowser.open("https://google.com")
            return "Opening Google."
        elif "weather" in command:
             webbrowser.open("https://www.google.com/search?q=weather+ankara")
             return "Checking weather."

        # API 
        elif "dollar" in command or "currency" in command:
            try:
                res = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
                return f"One dollar is {res['rates']['TRY']} liras."
            except:
                return "Currency Error."

        # LLM 
        elif self.llm_active:
            try:
                print(f"Sending to AI: {command}")
                response = self.model.generate_content(command)
                text = response.text.replace("*", "").replace("#", "")
                
                if len(text) > 300:
                    return text[:300] + "see screen for more"
                return text
            except Exception as e:
                print(f" AI Model Error: {e}")
                return "I am having trouble connecting to the AI model."
        
        return "I didn't understand."

