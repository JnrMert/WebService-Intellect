from flask import Flask, Response
import requests

app = Flask(__name__)

# Hedef URL
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx"

# 📌 Gelen XML verisini SOAP formatında alıp döndürme
@app.route("/", methods=["GET"])
def get_soap_response():
    # SOAP 1.1 İsteği
    soap_request = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                   xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                   xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <ExecuteTransaction xmlns="http://tempuri.org/Intellect/ExecuteTransaction">
                <Request>Test Request</Request>
            </ExecuteTransaction>
        </soap:Body>
    </soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://tempuri.org/Intellect/ExecuteTransaction/ExecuteTransaction"
    }

    # 📌 Hedef servise GET isteği yerine SOAP XML gönderimi yap
    response = requests.post(TARGET_URL, headers=headers, data=soap_request)

    # Gelen yanıtı döndür
    return Response(response.text, mimetype="text/xml", status=response.status_code)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
