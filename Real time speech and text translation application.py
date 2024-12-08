import os
import tkinter as tk
from tkinter import Button, Canvas, END, Label, OptionMenu, StringVar, Text, Tk, filedialog
from threading import Thread
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from playsound import playsound  # Changed from simpleaudio to playsound
from langdetect import detect
import tkinter.messagebox as tkMessageBox
from moviepy.editor import AudioFileClip

# Initialize the recognizer
r = sr.Recognizer()

main = Tk()
main.title("Real Time Voice and Text Translation Application")
main.geometry("960x850")
main.config(bg="#C7F8FF")
main.resizable(0, 0)

# Add new languages here
lt = ["English", "Hindi", "Tamil", "Gujarati", "Marathi", "Telugu", "Bengali", "Kannada", "Malayalam", "French", "Spanish", "German", "Chinese", "Japanese", "Russian",
      "Italian", "Portuguese", "Dutch", "Turkish", "Arabic", "Korean", "Swedish", "Norwegian", "Danish", "Polish", "Czech", "Urdu"]

# Language codes corresponding to the languages in lt
code = ["en", "hi", "ta", "gu", "mr", "te", "bn", "kn", "ml", "fr", "es", "de", "zh-CN", "ja", "ru",
        "it", "pt", "nl", "tr", "ar", "ko", "sv", "no", "da", "pl", "cs", "ur"]

v1 = StringVar(main)
v1.set(lt[0])
v2 = StringVar(main)
v2.set(lt[1])

Label(main, text="Translate Language via Voice Commands", font=("", 18, "bold"), bg="#C7F8FF", fg="black").place(x=240, y=20)

flag = False

Label(main, text="Input Box:", font=("", 12, "bold"), bg="#17C3B2", fg="black").place(x=44, y=60)
can1 = Canvas(main, width=400, height=450, bg="#17C3B2", relief="solid", bd=1, highlightthickness=0)
can1.place(x=30, y=80)

Label(main, text="Output Box:", font=("", 12, "bold"), bg="#17C3B2", fg="black").place(x=780, y=60)
can2 = Canvas(main, width=400, height=450, bg="#17C3B2", relief="solid", bd=1, highlightthickness=0)
can2.place(x=490, y=80)

txtbx = Text(main, width=40, height=7, font=("", 12, "bold"), relief="solid", bd=0, highlightthickness=0)
txtbx.place(x=50, y=100)

txtbx2 = Text(main, width=40, height=7, font=("", 12, "bold"), relief="solid", bd=0, highlightthickness=0)
txtbx2.place(x=510, y=100)

def speak():
    global txtbx2
    tx = txtbx2.get("1.0", END).strip()
    if not tx:
        tkMessageBox.showinfo("Warning", "Nothing to speak.")
        return
    language = code[lt.index(v2.get())]
    myobj = gTTS(text=tx, lang=language, slow=False)
    
    try:
        os.remove("temp.mp3")
    except Exception as e:
        print(f"Error removing temp.mp3: {e}")
    
    myobj.save("temp.mp3")
    
    # Use playsound to play the sound
    try:
        playsound("temp.mp3")
    except Exception as e:
        tkMessageBox.showinfo("Warning", f"Error playing audio: {e}")

def save_voice():
    tx = txtbx2.get("1.0", END).strip()
    if not tx:
        tkMessageBox.showinfo("Warning", "Nothing to save.")
        return
    language = code[lt.index(v2.get())]
    myobj = gTTS(text=tx, lang=language, slow=False)
    file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        myobj.save(file_path)

def translate():
    global txtbx, txtbx2
    txtbx2.delete("1.0", END)
    tx = txtbx.get("1.0", END).strip()
    if not tx:
        tkMessageBox.showinfo("Warning", "Nothing to translate.")
        return
    lang = code[lt.index(v2.get())]
    translator = Translator()
    translated = translator.translate(tx, dest=lang)
    txtbx2.insert(END, translated.text)

def detect_language(text):
    try:
        detected_lang = detect(text)
        if detected_lang in code:
            lang_name = lt[code.index(detected_lang)]
            v1.set(lang_name)
        else:
            tkMessageBox.showinfo("Warning", "Detected language is not supported.")
    except Exception as e:
        tkMessageBox.showinfo("Warning", f"Language detection failed: {e}")

def detect_voice():
    global flag, txtbx
    while not flag:
        try:
            with sr.Microphone() as source2:
                print("Listening...")
                r.adjust_for_ambient_noise(source2, duration=1)
                audio2 = r.listen(source2)
                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()
                txtbx.insert(END, MyText + "\n")
                detect_language(MyText)
        except sr.RequestError as e:
            tkMessageBox.showinfo("Warning", f"Could not request results; {e}")
            break
        except sr.UnknownValueError:
            tkMessageBox.showinfo("Warning", "Unknown error occurred")
            break
        except Exception as e:
            tkMessageBox.showinfo("Warning", f"An error occurred: {e}")

def start():
    global flag, b1
    flag = False
    b1["text"] = "Stop Speaking"
    b1["command"] = stop
    Thread(target=detect_voice).start()

def stop():
    global flag, b1
    b1["text"] = "Give Voice Input"
    b1["command"] = start
    flag = True

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read()
                txtbx.delete("1.0", END)
                txtbx.insert(END, file_content)
            detect_language(file_content)
        except Exception as e:
            tkMessageBox.showinfo("Error", f"Could not read the file: {e}")

def save_translated_text():
    translated_text = txtbx2.get("1.0", END).strip()
    if not translated_text:
        tkMessageBox.showinfo("Warning", "Nothing to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(translated_text)

def upload_audio_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3")])
    if file_path:
        try:
            # Convert MP3 to WAV if necessary
            if file_path.endswith(".mp3"):
                audio_clip = AudioFileClip(file_path)
                file_path_wav = "temp.wav"
                audio_clip.write_audiofile(file_path_wav, codec='pcm_s16le')
                file_path = file_path_wav

            # Process the audio file for speech recognition
            with sr.AudioFile(file_path) as source:
                audio = r.record(source)
                MyText = r.recognize_google(audio)
                print(f"Transcribed Text: {MyText}")
                txtbx.delete("1.0", END)
                txtbx.insert(END, MyText + "\n")
                detect_language(MyText)
                translate()  # Translate the extracted text
        except sr.RequestError as e:
            tkMessageBox.showinfo("Warning", f"Could not request results; {e}")
        except sr.UnknownValueError:
            tkMessageBox.showinfo("Warning", "Unknown error occurred")
        except Exception as e:
            tkMessageBox.showinfo("Warning", f"An error occurred: {e}")

b1 = Button(main, text="Give Voice Input", font=("", 12, "bold"), width=35, height=1, bg="#FEF9EF", fg="black", command=start, relief="solid", bd=4, highlightthickness=0)
b1.place(x=50, y=250)

Button(main, text="Upload Audio File", font=("", 12, "bold"), width=35, height=1, bg="#FEF9EF", fg="black", command=upload_audio_file, relief="solid", bd=4, highlightthickness=0).place(x=50, y=300)

Button(main, text="Speak Text", font=("", 12, "bold"), width=35, height=1, bg="#FEF9EF", fg="black", command=speak, relief="solid", bd=4, highlightthickness=0).place(x=510, y=250)
Button(main, text="Save Voice Output", font=("", 12, "bold"), width=35, height=1, bg="#FEF9EF", fg="black", command=save_voice, relief="solid", bd=4, highlightthickness=0).place(x=510, y=300)
Button(main, text="Translate", font=("", 15, "bold"), width=71, height=3, bg="#FEF9EF", fg="black", command=translate, relief="solid", bd=3, highlightthickness=0).place(x=30, y=446)
Button(main, text="Upload Text File", font=("", 12, "bold"), width=35, height=1, bg="#FEF9EF", fg="black", command=upload_file, relief="solid", bd=4, highlightthickness=0).place(x=50, y=500)
Button(main, text="Save Translated Text", font=("", 12, "bold"), width=35, height=1, bg="#FEF9EF", fg="black", command=save_translated_text, relief="solid", bd=4, highlightthickness=0).place(x=510, y=500)

# Language selection labels and option menus
Label(main, text="Select Input Language:", font=("", 12, "bold"), bg="#17C3B2", fg="black").place(x=50, y=340)
Label(main, text="Select Output Language:", font=("", 12, "bold"), bg="#17C3B2", fg="black").place(x=510, y=360)

o1 = OptionMenu(main, v1, *lt)
o1.config(font=("", 12, "bold"), width=36, bg="#FEF9EF", fg="black", relief="solid", bd=1, highlightthickness=0)
o1.place(x=50, y=370)

o2 = OptionMenu(main, v2, *lt)
o2.config(font=("", 12, "bold"), width=36, bg="#FEF9EF", fg="black", relief="solid", bd=1, highlightthickness=0)
o2.place(x=510, y=390)

main.mainloop()
