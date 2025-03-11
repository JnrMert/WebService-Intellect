from flask import Flask, request, Response
import requests
import logging

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx"

@app.route("/", methods=["GET"])
def home():
    return "XML Forwarder Çalışıyor - Debugging Aktif"

@app.route("/debug", methods=["GET", "POST"])
def debug_endpoint():
    """Gelen istekleri ve içeriklerini görüntüle"""
    
    output = "DEBUG BİLGİLERİ:\n\n"
    output += f"Method: {request.method}\n"
    output += f"Headers: {dict(request.headers)}\n\n"
    
    if request.method == 'POST':
        if 'application/x-www-form-urlencoded' in request.headers.get('Content-Type', ''):
            output += f"Form verileri: {dict(request.form)}\n\n"
        
        if request.data:
            output += f"Raw veri: {request.data.decode('utf-8')}\n\n"
    
    return Response(output, mimetype='text/plain')

@app.route("/", methods=["POST"])
def forward_xml():
    # Gelen veriyi yazdır
    logger.info("Yeni istek alındı")
    
    # İstek içeriğini kaydet
    content_type = request.headers.get('Content-Type', '')
    logger.info(f"Content-Type: {content_type}")
    
    # XML verisini al
    if 'application/x-www-form-urlencoded' in content_type:
        if 'Request' in request.form:
            xml_data = request.form['Request']
            logger.info(f"Form verisi alındı (Request): {xml_data}")
        else:
            all_form = dict(request.form)
            logger.info(f"Tüm form verileri: {all_form}")
            xml_data = str(all_form)
    else:
        try:
            xml_data = request.data.decode('utf-8')
            logger.info(f"Raw veri alındı: {xml_data}")
        except:
            xml_data = str(request.data)
            logger.info(f"Binary veri alındı: {xml_data[:100]}")
    
    # SOAP envelope oluştur
    soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <soap:Body>
    <ExecuteTransaction xmlns="http://tempuri.org/Intellect/ExecuteTransaction">
      <Request>{xml_data}</Request>
    </ExecuteTransaction>
  </soap:Body>
</soap:Envelope>"""
    
    # Gönderilen SOAP verisi
    logger.info(f"Gönderilen SOAP: {soap_envelope}")
    
    # İsteği gönder
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://tempuri.org/Intellect/ExecuteTransaction/ExecuteTransaction'
    }
    
    try:
        # İstek gönderiliyor
        logger.info(f"İstek gönderiliyor: URL={TARGET_URL}, Headers={headers}")
        response = requests.post(TARGET_URL, data=soap_envelope, headers=headers)
        
        # Yanıt bilgilerini yazdır
        logger.info(f"Yanıt durum kodu: {response.status_code}")
        logger.info(f"Yanıt başlıkları: {dict(response.headers)}")
        logger.info(f"Yanıt içeriği: {response.text}")
        
        # Yanıtı döndür
        return Response(
            f"""
            <html>
            <head><title>XML Forwarder Debug</title></head>
            <body>
                <h1>XML Forwarder Debug</h1>
                <h2>Gelen Veri:</h2>
                <pre>{xml_data}</pre>
                
                <h2>Gönderilen SOAP:</h2>
                <pre>{soap_envelope}</pre>
                
                <h2>Yanıt Durum Kodu:</h2>
                <pre>{response.status_code}</pre>
                
                <h2>Yanıt Başlıkları:</h2>
                <pre>{dict(response.headers)}</pre>
                
                <h2>Yanıt İçeriği:</h2>
                <pre>{response.text}</pre>
            </body>
            </html>
            """,
            mimetype='text/html'
        )
    
    except Exception as e:
        error_message = f"İstek gönderme hatası: {str(e)}"
        logger.error(error_message)
        return Response(
            f"""
            <html>
            <head><title>XML Forwarder Error</title></head>
            <body>
                <h1>Hata Oluştu</h1>
                <pre>{error_message}</pre>
                
                <h2>Gelen Veri:</h2>
                <pre>{xml_data}</pre>
            </body>
            </html>
            """,
            mimetype='text/html',
            status=500
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
