from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Hedef URL (Bu değişmeyecek)
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx/ExecuteTransaction"

@app.route("/", methods=["GET"])
def home():
    return Response(
        """<?xml version="1.0" encoding="UTF-8"?>
        <status>Flask XML Listener Çalışıyor</status>""",
        mimetype="text/xml"
    )

# 📌 XML POST edildiğinde hedefe yönlendirir
@app.route("/", methods=["POST"])
def receive_and_forward_xml():
    # Gönderilen XML verisini al
    xml_data = request.data.decode("utf-8")

    if not xml_data:
        return jsonify({"error": "Boş XML verisi gönderilemez!"}), 400

    # Hedef servise XML'i post et
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {"Request": xml_data}  # XML verisini x-www-form-urlencoded formatında gönder

    response = requests.post(TARGET_URL, headers=headers, data=payload)

    # Hedef sistemin cevabını döndür
    return jsonify({
        "sent_to": TARGET_URL,
        "status": response.status_code,
        "response": response.text
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
