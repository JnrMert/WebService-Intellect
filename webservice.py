from flask import Flask, jsonify
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx/ExecuteTransaction"

# Yükleme dizinini oluştur
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Dosya sistemi izleyici
class Watcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".xml"):
            self.send_xml(event.src_path)

    def send_xml(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            xml_data = file.read()

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(TARGET_URL, headers=headers, data={"Request": xml_data})

        print(f"XML gönderildi: {file_path}")
        print(f"Durum Kodu: {response.status_code}")
        print(f"Cevap: {response.text}")

# Watchdog için Observer başlatmak
def start_watching():
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_FOLDER, recursive=False)
    observer.start()
    print("Dinleme başlatıldı...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Flask route sadece servisi çalıştıracak
@app.route("/")
def home():
    return jsonify({"status": "Dinleme başlatıldı. Lütfen XML dosyası ekleyin."})

if __name__ == "__main__":
    # Watchdog'u başlat
    from threading import Thread
    thread = Thread(target=start_watching)
    thread.daemon = True
    thread.start()

    # Flask uygulamasını başlat
    app.run(host='0.0.0.0', port=5000, debug=False)
