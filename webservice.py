from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Hedef URL
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx/ExecuteTransaction"

# 📌 GET isteği sadece servisin çalıştığını kontrol eder
@app.route("/", methods=["GET"])
def home():
    return Response(
        """<?xml version="1.0" encoding="UTF-8"?>
        <status>Flask XML Listener Çalışıyor</status>""",
        mimetype="text/xml"
    )

# 📌 Gelen XML verisini SOAP formatında hedefe yönlendirir
@app.route("/", methods=["POST"])
def receive_and_forward_xml():
    xml_data = request.data.decode("utf-8")  # Gelen ham XML verisini al

    if not xml_data:
        return Response(
            """<?xml version="1.0" encoding="UTF-8"?>
            <error>Boş XML verisi gönderilemez!</error>""",
            mimetype="text/xml",
            status=400
        )

    # 📌 SOAP Formatına Uygun XML Şablonu
    soap_template = f"""<?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:int="http://test12.probizyazilim.com/Intellect/">
        <soapenv:Header/>
        <soapenv:Body>
            <int:ExecuteTransaction>
                <int:Request>{xml_data}</int:Request>
            </int:ExecuteTransaction>
        </soapenv:Body>
    </soapenv:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://test12.probizyazilim.com/Intellect/ExecuteTransaction"
    }

    # Hedef servise SOAP XML gönderimi
    response = requests.post(TARGET_URL, headers=headers, data=soap_template)

    return Response(response.text, mimetype="text/xml", status=response.status_code)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
