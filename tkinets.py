import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import speech_recognition as sr
from PIL import Image, ImageTk
from googletrans import Translator  # Import Translator from googletrans library
from io import BytesIO

# Create a translator object
translator = Translator()


def speech_to_text():
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Open the microphone and capture audio
    with sr.Microphone() as source:
        print("Please start speaking...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source, timeout=10)  # Listen for up to 10 seconds

    try:
        # Use Google Web Speech API to recognize the audio
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said.")
    except sr.RequestError as e:
        print(f"Sorry, an error occurred during the request: {e}")

    return None

def generate_image(prompt):
    
    url = f"https://image.pollinations.ai/prompt/{prompt},32k,uhd,ultra realistic,blurless,realistic"

    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        content = response.content
    
        # Specify the file name and extension (e.g., "image.jpg")
        file_name = "image.jpg"
        
        # Save the binary content to a file
        with open(file_name, "wb") as file:
            file.write(content)
        return file_name
    else:
        return None

def translate_to_english(text, source_language):
    # Translate the given text to English using the translator object
    translation = translator.translate(text, src=source_language, dest="en")
    return translation.text

def recognize_speech():
    result = speech_to_text()

    if result:
        detected_language = translator.detect(result).lang
        translated_text = translate_to_english(result, detected_language)
        recognized_text.set(translated_text)
        original_text.set(result)
        app.update_idletasks()
        display_generated_image()

def display_generated_image():
    result = generate_image(recognized_text.get())
    if result:
        image = Image.open(result)
        photo = ImageTk.PhotoImage(image)
        generated_image_label.config(image=photo)
        generated_image_label.photo = photo
        generated_image_bytes = BytesIO()
        image.save(generated_image_bytes, format="PNG")
        generated_image_bytes.seek(0)
        return generated_image_bytes
    else:
        messagebox.showerror("Error", "Image generation failed.")

def save_image():
    generated_image_bytes = display_generated_image()
    if generated_image_bytes:
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            with open(file_path, "wb") as image_file:
                image_file.write(generated_image_bytes.read())
            messagebox.showinfo("Image Saved", f"Generated image has been saved as '{file_path}'.")

app = tk.Tk()
app.title("Voice2Visual")

logo_image = tk.PhotoImage(file="logo.png")
logo_label = tk.Label(app, image=logo_image)
logo_label.pack()

generate_button = tk.Button(app, text="Generate Image", command=recognize_speech)

original_text = tk.StringVar()
original_text_label = tk.Label(app, text="Original Text:")
original_text_display = tk.Label(app, textvariable=original_text, wraplength=400)

recognized_text = tk.StringVar()
text_label = tk.Label(app, text="Translated Text:")
text_display = tk.Label(app, textvariable=recognized_text, wraplength=400)

generated_image_label = tk.Label(app)

save_image_button = tk.Button(app, text="Save Image", command=save_image)

generate_button.pack()
original_text_label.pack()
original_text_display.pack()
text_label.pack()
text_display.pack()
generated_image_label.pack()
save_image_button.pack()

app.mainloop()