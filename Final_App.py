#import packages
from gtts import gTTS, lang
import os
from tkinter import *
from tkinter import messagebox
import speech_recognition as sr
from io import BytesIO
from playsound import playsound
from googletrans import Translator
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from pydub import AudioSegment
import threading

stop_listening = False
counter = 0
running = False
recognized_text_all = ""
VOICE_EFFECTS = [
    "Chipmunk",
    "Robot",
    "Slow Motion",
    "Fast Forward",
    "Echo",
    "Deep Voice",
    "Whisper",
    "Bass Boost"
]

#define functions
#text to speech conversion
def text_to_speech():
    # Read inputs given by the user
    translator = Translator()
    text = text_entry.get("1.0", "end-1c")
    language = accent_combobox.get()  
    speed = True if speed_combobox.get() == "slow" else False
    
    # Check if the user submitted inputs
    if len(text) <= 1 or len(language) <= 0:
        messagebox.showerror(message="Enter required details")
        return

    try:
        # Translate the text
        translated = translator.translate(text, src='vi', dest=language).text
        
        # Ensure the translated text is a string
        if not isinstance(translated, str):
            raise ValueError("The translated text is not a valid string")
        
        # Convert the translated text to speech
        speech = gTTS(text=translated, lang=language, slow=speed)
        
        if os.path.exists('output.mp3'):
             os.remove('output.mp3')
        speech.save("output.mp3")
        
        playsound("output.mp3")
    
    except Exception as e:
        messagebox.showerror(message=f"Error: {str(e)}")

#List the supported languages and their keys
def list_languages():
    # Lấy danh sách các ngôn ngữ và mã từ gtts.langs
    languages = lang.tts_langs()
    return [f"{key} {value}" for key, value in languages.items()]

# Thêm nút hiển thị ngôn ngữ đã chọn
def show_selected_language():
    selected = accent_combobox.get() 
    if selected:
        # Tìm tên ngôn ngữ từ danh sách ban đầu
        languages = lang.tts_langs()  # Lấy danh sách mã ngôn ngữ và tên
        language_name = languages.get(selected, "Không xác định")
        messagebox.showinfo("Ngôn ngữ đã chọn", f"Mã ngôn ngữ: {selected}\nNgôn ngữ: {language_name}")
    else:
        messagebox.showinfo("Ngôn ngữ đã chọn", "Không có lựa chọn")

# Hàm xử lý khi chọn ngôn ngữ
def update_combobox_value(event):
    selected = accent_combobox.get()
    # Lấy phần key
    language_key = selected.split(' ')[0] if selected else ""
    # Cập nhật giá trị trong Combobox
    accent_combobox.set(language_key)

# Hàm cập nhật giá trị hiển thị trong combobox
def update_speed_value(event):
    selected_speed = speed_combobox.get()
    if selected_speed:
        # Lấy phần key (fast hoặc slow)
        speed_key = selected_speed.split(' - ')[0]
        # Đặt giá trị key vào combobox
        speed_combobox.set(speed_key)

# Hàm cập nhật giá trị hiển thị trong combobox
def update_voice_value(event):
    selected_voice = voice_combobox.get()
    if selected_voice:
        speed_combobox.set(selected_voice)

def show_speech_to_text():
    # Hàm dừng nhận diện
    def finish_recognition():
        global stop_listening, running
        stop_listening = True
        running = False
        status_label.config(text="Đã kết thúc ghi âm.")

    def update_counter():
        global counter, running
        if running:
            counter_label.config(text=f"Thời gian: {counter} giây")
            counter += 1
            popupSTT.after(1000, update_counter)
    # Hàm xử lý khi nhấn nút Import
    def import_text():
        text_entry.delete("1.0", tk.END) 
        text_entry.insert("1.0", text_box.get("1.0", "end-1c")) 
        popupSTT.destroy() 
    
    # Hàm nhận diện giọng nói
    def start_recognition():
        global stop_listening, counter, running, recognized_text_all
        stop_listening = False
        counter = 0
        running = True
        recognized_text_all = ""  # Reset khi bắt đầu ghi âm mới
        text_box.delete(1.0, tk.END)
        update_counter()
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            status_label.config(text="Đang lắng nghe...")
            popupSTT.update_idletasks()
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
            # Lặp vô hạn để tiếp tục nghe cho đến khi nhấn nút "Kết thúc"
                while not stop_listening:
                    audio = recognizer.listen(source)
                    try:
                        # Nhận diện đoạn văn mới và nối vào toàn bộ văn bản
                        recognized_text = recognizer.recognize_google(audio, language="vi-VN")
                        recognized_text_all += " " + recognized_text  # Nối đoạn văn nhận diện
                        # Hiển thị toàn bộ đoạn văn
                        text_box.config(state=tk.NORMAL)  # Cho phép chỉnh sửa nội dung của text box
                        text_box.delete(1.0, tk.END)  
                        text_box.insert(tk.END, recognized_text_all)  
                        text_box.config(state=tk.DISABLED)  # Tắt chế độ chỉnh sửa
                    except sr.UnknownValueError:
                        status_label.config(text="Không thể nhận diện âm thanh. Đang tiếp tục lắng nghe...")
                    except sr.RequestError as e:
                        messagebox.showerror("Lỗi", f"Lỗi API Google: {e}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi không xác định: {e}")
            finally:
                running = False
                status_label.config(text="Nhấn 'Bắt đầu' để thử lại")
                stop_listening = True
    
    popupSTT = tk.Toplevel()
    popupSTT.title("Speech To Text")
    # Thiết lập kích thước cửa sổ popup
    popup_width = window.winfo_width()  
    popup_height = window.winfo_height()
    popupSTT.geometry(f"{popup_width}x{popup_height}")
     # Cấu hình theme cho cửa sổ popup
    popup_style = ttk.Style()
    popup_style.configure("TLabel", font=('Segoe UI', 10))
    popup_style.configure("Title.TLabel", 
                          font=('Segoe UI', 14, 'bold'), 
                          foreground='#333333')
    popup_style.configure("TButton", 
                          font=('Segoe UI', 10), 
                          padding=6)
    popup_style.map('TButton', 
                    foreground=[('active', '#FFFFFF')],
                    background=[('active', '#4CAF50')])
    # Tiêu đề
    title_label = tk.Label(popupSTT, text="Nhận diện giọng nói tiếng Việt", font=("Arial", 16))
    title_label.pack(pady=10)

    start_button = tk.Button(popupSTT, text="Bắt đầu", font=("Arial", 14), command=lambda: threading.Thread(target=start_recognition).start())
    start_button.pack(pady=5)

    finish_button = tk.Button(popupSTT, text="Kết thúc", font=("Arial", 14), command=finish_recognition)
    finish_button.pack(pady=5)

    start_button = tk.Button(popupSTT, text="Import", font=("Arial", 14), command=import_text)
    start_button.pack(pady=5)

    counter_label = tk.Label(popupSTT, text="Thời gian: 0 giây", font=("Arial", 12))
    counter_label.pack(pady=10)

    status_label = tk.Label(popupSTT, text="Nhấn 'Bắt đầu' để sử dụng", font=("Arial", 12))
    status_label.pack(pady=10)

    # Text box để hiển thị toàn bộ văn bản nhận diện
    text_box = tk.Text(popupSTT, height=10, width=50, font=("Arial", 12))
    text_box.pack(pady=10)
    text_box.config(state=tk.DISABLED)  # Vô hiệu hóa chỉnh sửa trong text box

def show_transcribe_popup(transcribed_text):
    # Tạo cửa sổ popup theo theme của ứng dụng
    popup = tk.Toplevel()
    popup.title("Kết quả Transcribe")
    
    # Thiết lập kích thước cửa sổ popup
    popup_width = window.winfo_width()  
    popup_height = window.winfo_height()
    popup.geometry(f"{popup_width}x{popup_height}")

    # Cấu hình theme cho cửa sổ popup
    popup_style = ttk.Style()
    popup_style.configure("TLabel", font=('Segoe UI', 10))
    popup_style.configure("Title.TLabel", 
                          font=('Segoe UI', 14, 'bold'), 
                          foreground='#333333')
    popup_style.configure("TButton", 
                          font=('Segoe UI', 10), 
                          padding=6)
    popup_style.map('TButton', 
                    foreground=[('active', '#FFFFFF')],
                    background=[('active', '#4CAF50')])

    # Tiêu đề
    title_label = ttk.Label(popup, text="Văn bản đã chuyển đổi:", style="Title.TLabel")
    title_label.pack(pady=10)

    # Hộp văn bản để hiển thị kết quả
    text_box = tk.Text(popup, height=10, font=("Consolas", 10), wrap=tk.WORD, borderwidth=2, relief=tk.GROOVE)
    text_box.insert("1.0", transcribed_text)
    text_box.configure(state="disabled")  # Chỉ đọc
    text_box.pack(padx=10, pady=10, fill="both", expand=True)

    # Hàm xử lý khi nhấn nút Import
    def import_text():
        text_entry.delete("1.0", tk.END)  
        text_entry.insert("1.0", transcribed_text)  
        popup.destroy()  

    import_button = ttk.Button(popup, text="Import", command=import_text)
    import_button.pack(side="left", padx=20, pady=10, anchor="center")

    done_button = ttk.Button(popup, text="Done", command=popup.destroy)
    done_button.pack(side="right", padx=20, pady=10, anchor="center")

def transcribe_audio():
    file_path = filedialog.askopenfilename(
        title="Chọn tệp âm thanh",
        filetypes=[("Audio Files", "*.mp3 *.wav"), ("All Files", "*.*")]
    )
    
    if not file_path:
        messagebox.showinfo("Thông báo", "Bạn chưa chọn tệp âm thanh!")
        return

    # Kiểm tra định dạng file, nếu là MP3 thì chuyển sang WAV
    if file_path.endswith(".mp3"):
        wav_path = file_path.replace(".mp3", ".wav")
        try:
            audio = AudioSegment.from_mp3(file_path)
            audio.export(wav_path, format="wav")
            file_path = wav_path  # Cập nhật đường dẫn file WAV mới
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chuyển đổi MP3 sang WAV:\n{str(e)}")
            return

    # Sử dụng SpeechRecognition để transcribe file WAV
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="vi-VN")
            # Hiển thị văn bản đã chuyển đổi
            show_transcribe_popup(text)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể xử lý tệp âm thanh:\n{str(e)}")

def show_translate_popup():
    def translate_text():
        text = source_text.get("1.0", "end-1c")
        if len(text) <= 0:
            messagebox.showerror("Lỗi", "Vui lòng nhập văn bản cần dịch.")
            return
        # Lấy ngôn ngữ nguồn từ combobox
        source_language = source_combobox.get().split(' ')[0]
        # Lấy ngôn ngữ đích từ combobox dịch
        target_language = target_combobox.get().split(' ')[0] 

        if source_language == "Select Source Language":
            messagebox.showerror("Lỗi", "Vui lòng chọn ngôn ngữ hiện tại.")
            return
        if target_language == "Select Target Language":
            messagebox.showerror("Lỗi", "Vui lòng chọn ngôn ngữ đích.")
            return
            
        try:
            translator = Translator()

        # Dịch văn bản
            translated = translator.translate(text, src=source_language, dest=target_language).text
        
            target_text.delete("1.0", tk.END)
            target_text.insert("1.0", translated)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể dịch văn bản:\n{str(e)}")

    def import_text():
        text_entry.delete("1.0", tk.END)
        text_entry.insert("1.0", target_text.get("1.0", "end-1c"))  
        popup_window.destroy()
        
    # Tạo cửa sổ mới cho việc dịch
    popup_window = tk.Toplevel()
    popup_window.title("Translate Text")

    # Lấy kích thước màn hình và đặt kích thước cửa sổ
    popup_width = window.winfo_width() * 2
    popup_height = window.winfo_height()
    popup_window.geometry(f"{popup_width}x{popup_height}")

    # Style cho popup
    style = ttk.Style()
    style.configure("TLabel", font=('Segoe UI', 10))
    style.configure("TButton", font=('Segoe UI', 10), padding=6)
    style.map('TButton', foreground=[('active', '#FFFFFF')], background=[('active', '#4CAF50')])

    # Nhãn và ô nhập liệu cho văn bản cần dịch
    source_label = ttk.Label(popup_window, text="Nhập văn bản cần dịch:")
    source_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

    source_text = tk.Text(popup_window, font=('Consolas', 10), wrap=tk.WORD, borderwidth=2, relief=tk.GROOVE)
    source_text.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

    button_trans = ttk.Frame(popup_window)
    button_trans.grid(row=1, column=1, columnspan=1, pady=10)
    # Buttons
    button = ttk.Button(
    button_trans, 
    text="Trans",
    command=translate_text
)
    button.pack(side=tk.LEFT, padx=5)

    button2 = ttk.Button(
    button_trans, 
    text="Import",
    command=import_text
)
    button2.pack(side=tk.LEFT, padx=5)


    # Nhãn và ô nhập liệu cho văn bản dịch
    target_label = ttk.Label(popup_window, text="Bản dịch:")
    target_label.grid(row=0, column=2, padx=10, pady=10, sticky='w')

    target_text = tk.Text(popup_window, font=('Consolas', 10), wrap=tk.WORD, borderwidth=2, relief=tk.GROOVE)
    target_text.grid(row=1, column=2, padx=10, pady=10, sticky='nsew')

    popup_window.grid_columnconfigure(0, weight=1)
    popup_window.grid_columnconfigure(1, weight=1)
    popup_window.grid_columnconfigure(2, weight=1)
    popup_window.grid_rowconfigure(1, weight=1)

    # Combobox cho ngôn ngữ nguồn
    language_list = list_languages()
    source_combobox = ttk.Combobox(popup_window, values=language_list, state="readonly")
    source_combobox.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
    source_combobox.set("Select Source Language")

    # Combobox cho ngôn ngữ đích
    target_combobox = ttk.Combobox(popup_window, values=language_list, state="readonly")
    target_combobox.grid(row=2, column=2, padx=10, pady=10, sticky='ew')
    target_combobox.set("Select Target Language")



#Invoke call to class to view a window
window = tk.Tk()
window.title("Speech And Text Tool")

# Get screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Set window size to half the screen
window_width = screen_width // 2
window_height = screen_height // 2
window.geometry(f"{window_width}x{window_height}")

# Make window resizable
window.resizable(True, True)

# Configure grid layout for responsiveness
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(5, weight=1)

# Style configuration for modern look
style = ttk.Style()
style.theme_use('clam')
style.configure("TLabel", font=('Segoe UI', 10))
style.configure("Title.TLabel", 
                font=('Segoe UI', 16, 'bold'), 
                foreground='#333333')
style.configure("TButton", 
                font=('Segoe UI', 10), 
                padding=6)
style.map('TButton', 
          foreground=[('active', '#FFFFFF')],
          background=[('active', '#4CAF50')])

# Title Label (using grid)
title_label = ttk.Label(
    window, 
    text="Final App", 
    style="Title.TLabel"
)
title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky='ew')

# Text Input
text_label = ttk.Label(window, text="Text:")
text_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

text_entry = tk.Text(
    window, 
    height=10, 
    font=('Consolas', 10),
    wrap=tk.WORD,
    borderwidth=2,
    relief=tk.GROOVE
)
text_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

# Language Accent Dropdown
language_list = list_languages()
accent_label = ttk.Label(window, text="Accent:")
accent_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')

accent_combobox = ttk.Combobox(
    window, 
    values=language_list, 
    state="readonly"
)
accent_combobox.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
accent_combobox.set("Select Language")
accent_combobox.bind("<<ComboboxSelected>>", update_combobox_value)

# Speed Dropdown
speed_label = ttk.Label(window, text="Speed:")
speed_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')

speed_combobox = ttk.Combobox(
    window, 
    values=["fast - Nhanh", "slow - Chậm"], 
    state="readonly"
)
speed_combobox.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
speed_combobox.set("Select Speed")
speed_combobox.bind("<<ComboboxSelected>>", update_speed_value)

# voice Dropdown
voice_label = ttk.Label(window, text="Voice:")
voice_label.grid(row=4, column=0, padx=10, pady=5, sticky='w')

voice_combobox = ttk.Combobox(
    window, 
    values=VOICE_EFFECTS, 
    state="readonly"
)
voice_combobox.grid(row=4, column=1, padx=10, pady=10, sticky='ew')
voice_combobox.set("Select voice")
voice_combobox.bind("<<ComboboxSelected>>", update_voice_value)

# Buttons Frame
button_frame = ttk.Frame(window)
button_frame.grid(row=5, column=0, columnspan=2, pady=10)

# Buttons
button1 = ttk.Button(
    button_frame, 
    text="Show Language", 
    command=show_selected_language
)
button1.pack(side=tk.LEFT, padx=5)

button2 = ttk.Button(
    button_frame, 
    text='Text to Speech', 
    command=text_to_speech
)
button2.pack(side=tk.LEFT, padx=5)

button3 = ttk.Button(
    button_frame, 
    text='Speech to Text', 
    command=show_speech_to_text
)
button3.pack(side=tk.LEFT, padx=5)

button4 = ttk.Button(
    button_frame, 
    text='Audio to Text', 
    command=transcribe_audio
)
button4.pack(side=tk.LEFT, padx=5)

button5 = ttk.Button(
    button_frame, 
    text='Translate', 
    command=show_translate_popup
)
button5.pack(side=tk.LEFT, padx=5)

#close the app
window.mainloop()
