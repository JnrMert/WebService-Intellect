from flask import Flask, request, Response
import requests
from zeep import Client
from zeep.transports import Transport

app = Flask(__name__)

# Hedef WSDL URL - WSDL bulamazsanız doğrudan SOAP endpoint kullanacağız
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx"
SOAP_ACTION = "http://tempuri.org/Intellect/ExecuteTransaction/ExecuteTransaction"

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
    # İstek türünü kontrol et
    content_type = request.headers.get('Content-Type', '')
    
    # Form verisinden XML'i al (x-www-form-urlencoded için)
    if 'application/x-www-form-urlencoded' in content_type and 'Request' in request.form:
        xml_data = request.form['Request']
        print(f"Form verisi alındı: {xml_data[:100]}...")
    # Direkt raw veriden XML'i al
    elif request.data:
        xml_data = request.data.decode("utf-8")
        print(f"Raw veri alındı: {xml_data[:100]}...")
    else:
        return Response(
            """<?xml version="1.0" encoding="UTF-8"?>
            <error>Boş XML verisi gönderilemez!</error>""",
            mimetype="text/xml",
            status=400
        )
    
    # Yöntem 1: Doğrudan SOAP isteği (requests ile)
    try:
        # SOAP Envelope oluştur
        soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <ExecuteTransaction xmlns="http://tempuri.org/Intellect/ExecuteTransaction">
            <Request>{xml_data}</Request>
        </ExecuteTransaction>
    </soap:Body>
</soap:Envelope>"""

        print(f"Gönderiyor: {soap_envelope[:200]}...")
        
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": SOAP_ACTION
        }
        
        response = requests.post(TARGET_URL, headers=headers, data=soap_envelope)
        
        print(f"Yanıt Kodu: {response.status_code}")
        print(f"Yanıt: {response.text[:200]}...")
        
        if response.status_code == 200:
            return Response(response.text, mimetype="text/xml")
        else:
            print(f"Hata yanıtı: {response.text}")
            
            # Yöntem 2: Zeep ile deneyelim
            try:
                # Zeep transport oluştur
                transport = Transport()
                client = Client(wsdl=f"{TARGET_URL}?WSDL", transport=transport)
                
                # Servis metodunu çağır
                result = client.service.ExecuteTransaction(Request=xml_data)
                return Response(str(result), mimetype="text/xml")
            except Exception as zeep_error:
                print(f"Zeep hatası: {str(zeep_error)}")
                return Response(
                    f"""<?xml version="1.0" encoding="UTF-8"?>
                    <error>İki yöntem de başarısız oldu: {str(zeep_error)}</error>""",
                    mimetype="text/xml",
                    status=500
                )
            
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
