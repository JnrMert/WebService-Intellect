from flask import Flask, jsonify, request
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
TARGET_URLS = {
    "egt3": "http://egt3.probizyazilim.com/Intellect/ExecuteTransaction.asmx/ExecuteTransaction",
    "test12": "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx/ExecuteTransaction",
    "test20": "http://test20.probizyazilim.com/Intellect/ExecuteTransaction.asmx/ExecuteTransaction"
}
selected_target = "test12"  # Varsayılan hedef

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
        global selected_target
        target_url = TARGET_URLS[selected_target]

        with open(file_path, "r", encoding="utf-8") as file:
            xml_data = file.read()

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(target_url, headers=headers, data={"Request": xml_data})

        print(f"\n🔹 XML Gönderildi: {file_path}")
        print(f"📌 Hedef URL: {target_url}")
        print(f"✅ Durum Kodu: {response.status_code}")
        print(f"📜 Cevap: {response.text}")

# Watchdog için Observer başlatmak
def start_watching():
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_FOLDER, recursive=False)
    observer.start()
    print("🔍 XML dinleme başlatıldı...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Dinleme başlatıldığında geri bildirim endpoint'i
@app.route("/")
def home():
    return jsonify({"status": "Dinleme başlatıldı", "current_target": selected_target})

# Hedef URL'yi değiştirmek için API
@app.route("/set_target", methods=["POST"])
def set_target():
    global selected_target
    data = request.json
    new_target = data.get("target")

    if new_target in TARGET_URLS:
        selected_target = new_target
        return jsonify({"message": f"Hedef {new_target} olarak değiştirildi!", "new_target": new_target})
    else:
        return jsonify({"error": "Geçersiz hedef adı!"}), 400

if __name__ == "__main__":
    # Watchdog'u başlat
    from threading import Thread
    thread = Thread(target=start_watching)
    thread.daemon = True
    thread.start()

    # Flask uygulamasını başlat
    app.run(host="0.0.0.0", port=5000, debug=False)
