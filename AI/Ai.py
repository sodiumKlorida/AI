import speech_recognition as srec
import pygame
from flask import Flask, render_template, request
from gtts import gTTS
from groq import Groq
import io
import os
from translate import Translator

app = Flask(__name__)

# Fungsi untuk mengenali perintah suara
def perintah():
    mendengar = srec.Recognizer()
    with srec.Microphone() as source:
        print('Mendengarkan....')
        suara = mendengar.listen(source, phrase_time_limit=5)
        try:
            print('Diterima...')
            dengar = mendengar.recognize_google(suara, language='id-ID')
            print(dengar)
        except Exception:
            dengar = "silent"
        return dengar
        
def ngomong(teks):
    bahasa = 'id'
    suara = gTTS(text=teks, lang=bahasa, slow=False)
    mp3_fp = io.BytesIO()
    suara.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp, 'mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def stop_baca():
    if pygame.mixer.get_init():  # Cek apakah pygame sudah diinisialisasi
        pygame.mixer.music.stop()

def bersihkan_teks(teks):
    teks_bersih = teks.replace("~", "").replace("<", "").replace(">", "").replace("*", "")
    return teks_bersih

def proses_dengan_groq(teks):
    api_key = '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'  # Ganti dengan kunci API Anda yang sebenarnya
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": teks
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    return completion


# Fungsi utama untuk menjalankan program
def run_michelle():
    Layanan = perintah()
    if Layanan:
        respon = proses_dengan_groq(Layanan)
        if respon.choices:
            
            respon_text = respon.choices[0].message.content  # Mengambil konten dari respons Groq
            clean = bersihkan_teks(respon_text)
            print( clean)
            return clean, Layanan
        else:
            print("Tidak ada respons yang diterima dari Groq.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hasil', methods=['POST'])
def hasil():
    clean_text, Layanan = run_michelle()  # Unpack the tuple returned by run_michelle()
    return render_template('hasil.html', clean=clean_text, layanan=Layanan)

@app.route('/baca', methods=['POST'])
def baca():
    # Ambil teks dari form POST
    clean_text = request.form['clean']
    ngomong(clean_text)  # Panggil fungsi ngomong() untuk membacakan teks
    return render_template('hasil.html', clean=clean_text)

@app.route('/stop', methods=['POST'])
def stop():
    stop_baca()  # Panggil fungsi stop_baca() untuk menghentikan pembacaan
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)