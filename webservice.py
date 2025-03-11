from flask import Flask, request, Response
import requests
import xml.etree.ElementTree as ET
import re

app = Flask(__name__)
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx"

# XML yanıtını temizleyen fonksiyon
def clean_xml_response(xml_text):
    # Bazı temel temizleme işlemleri
    # BOM karakterlerini temizle
    if xml_text.startswith('\ufeff'):
        xml_text = xml_text[1:]
    
    # XML bildirimini düzelt (gerekirse)
    if not xml_text.startswith('<?xml'):
        xml_text = '<?xml version="1.0" encoding="utf-8"?>' + xml_text
    
    # Geçersiz karakterleri temizle
    xml_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_text)
    
    return xml_text

@app.route("/", methods=["GET"])
def home():
    return "XML Forwarder Çalışıyor"

@app.route("/", methods=["POST"])
def forward_xml():
    try:
        # Content-Type kontrolü
        content_type = request.headers.get('Content-Type', '')
        
        # Form verisi kontrolü
        if 'application/x-www-form-urlencoded' in content_type and 'Request' in request.form:
            client_data = request.form['Request']
            print(f"Form verisi alındı: {client_data[:100]}...")
        else:
            client_data = request.data.decode('utf-8')
            print(f"Raw veri alındı: {client_data[:100]}...")
        
        # SOAP XML şablonu
        soap_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <soap:Body>
    <ExecuteTransaction xmlns="http://tempuri.org/Intellect/ExecuteTransaction">
      <Request>{client_data}</Request>
    </ExecuteTransaction>
  </soap:Body>
</soap:Envelope>"""
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://tempuri.org/Intellect/ExecuteTransaction/ExecuteTransaction'
        }
        
        # İsteği gönder
        response = requests.post(TARGET_URL, data=soap_xml, headers=headers)
        
        print(f"Yanıt Kodu: {response.status_code}")
        print(f"Yanıt başlığı: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                # Yanıtı temizle
                clean_response = clean_xml_response(response.text)
                
                # XML'i ayrıştır (test amaçlı)
                try:
                    ET.fromstring(clean_response)
                    print("XML doğrulama başarılı!")
                except Exception as xml_error:
                    print(f"XML ayrıştırma hatası: {str(xml_error)}")
                
                # SOAP zarfından içeriği çıkarma denemesi
                try:
                    # Basit bir regex yaklaşımı
                    result_match = re.search(r'<ExecuteTransactionResult>(.*?)</ExecuteTransactionResult>', clean_response, re.DOTALL)
                    if result_match:
                        result_content = result_match.group(1)
                        print(f"Çıkarılan içerik: {result_content[:100]}...")
                        return Response(result_content, mimetype='text/xml')
                except Exception as e:
                    print(f"İçerik çıkarma hatası: {str(e)}")
                
                # Temizlenmiş yanıtı gönder
                return Response(clean_response, mimetype='text/xml')
            except Exception as parsing_error:
                print(f"Yanıt temizleme hatası: {str(parsing_error)}")
                return Response(response.text, mimetype='text/plain')
        else:
            return Response(
                f"<error>Servis hatası: HTTP {response.status_code}</error>",
                mimetype='text/xml', 
                status=response.status_code
            )
            
    except Exception as e:
        error_message = f"İşlem hatası: {str(e)}"
        print(error_message)
        return Response(f"<error>{error_message}</error>", mimetype='text/xml', status=500)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
