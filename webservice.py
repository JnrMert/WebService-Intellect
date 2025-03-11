from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Hedef URL
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx/ExecuteTransaction"

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

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "Request": xml_data  # Hedef servisin beklediği format
    }

    # Hedef servise gönderim
    response = requests.post(TARGET_URL, headers=headers, data=payload)

    # Gelen yanıtı döndür
    return Response(response.text, mimetype="text/xml", status=response.status_code)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
