from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Hedef URL
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx"

# 📌 GET isteği servisin çalıştığını kontrol eder
@app.route("/", methods=["GET"])
def home():
    return Response(
        """<?xml version="1.0" encoding="UTF-8"?>
        <status>Flask XML Listener Çalışıyor</status>""",
        mimetype="text/xml"
    )

# 📌 Gelen XML verisini alıp SOAP formatında hedefe yönlendirir
@app.route("/", methods=["POST"])
def receive_and_forward_xml():
    # Form verisinden XML'i al (x-www-form-urlencoded için)
    if request.form and 'Request' in request.form:
        xml_data = request.form['Request']
    # Direkt raw veriden XML'i al
    elif request.data:
        xml_data = request.data.decode("utf-8")
    else:
        return Response(
            """<?xml version="1.0" encoding="UTF-8"?>
            <error>Boş XML verisi gönderilemez!</error>""",
            mimetype="text/xml",
            status=400
        )
    
    # XML içeriğini temizle
    xml_data = xml_data.strip()
    
    # 📌 Servisin beklediği SOAP 1.1 formatına uygun XML şablonu
    soap_template = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                   xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                   xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <ExecuteTransaction xmlns="http://tempuri.org/Intellect/ExecuteTransaction">
                <Request>{xml_data}</Request>
            </ExecuteTransaction>
        </soap:Body>
    </soap:Envelope>"""
    
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://tempuri.org/Intellect/ExecuteTransaction/ExecuteTransaction"
    }
    
    try:
        # Hedef servise SOAP XML gönderimi
        response = requests.post(TARGET_URL, headers=headers, data=soap_template)
        
        # Yanıt durumunu logla
        print(f"Yanıt Kodu: {response.status_code}")
        print(f"Yanıt: {response.text[:200]}...")
        
        return Response(response.text, mimetype="text/xml", status=response.status_code)
    except Exception as e:
        error_message = f"Hata oluştu: {str(e)}"
        print(error_message)
        return Response(
            f"""<?xml version="1.0" encoding="UTF-8"?>
            <error>{error_message}</error>""",
            mimetype="text/xml",
            status=500
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
