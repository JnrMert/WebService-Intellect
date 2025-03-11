from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

# Hedef URL
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx/ExecuteTransaction"

# Log klasörü oluştur
LOG_FOLDER = "logs"
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

LOG_FILE = os.path.join(LOG_FOLDER, "received_xml.log")

# 📌 Gelen XML'i kaydetmek için fonksiyon
def log_data(data, response_text):
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write("\n--- Yeni İstek ---\n")
        log_file.write(f"Gelen XML:\n{data}\n")
        log_file.write(f"Servisten Gelen Yanıt:\n{response_text}\n")
        log_file.write("-" * 50 + "\n")

# 📌 GET isteği servisin çalıştığını kontrol eder
@app.route("/", methods=["GET"])
def home():
    return Response(
        """<?xml version="1.0" encoding="UTF-8"?>
        <status>Flask XML Listener Çalışıyor</status>""",
        mimetype="text/xml"
    )

# 📌 Gelen XML verisini hedefe yönlendirir
@app.route("/", methods=["POST"])
def receive_and_forward_xml():
    xml_data = request.data.decode("utf-8")  # Gelen XML verisini al

    if not xml_data:
        return Response(
            """<?xml version="1.0" encoding="UTF-8"?>
            <error>Boş XML verisi gönderilemez!</error>""",
            mimetype="text/xml",
            status=400
        )

    print("\n--- Gelen XML ---")
    print(xml_data)  # Terminale yazdır

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "Request": xml_data  # Hedef servisin beklediği format
    }

    # Hedef servise gönderim
    response = requests.post(TARGET_URL, headers=headers, data=payload)

    # Yanıtı logla
    print("\n--- Servisten Gelen Yanıt ---")
    print(response.text)

    log_data(xml_data, response.text)  # XML'i ve yanıtı dosyaya kaydet

    # Gelen yanıtı döndür
    return Response(response.text, mimetype="text/xml", status=response.status_code)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
