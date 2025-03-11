from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
import html

app = Flask(__name__)

@app.route('/receive_soap', methods=['POST'])
def receive_soap():
    # Gelen veriyi al
    soap_data = request.data.decode('utf-8')
    
    # Log olarak gelen veriyi kaydet
    with open('soap_request_log.xml', 'w', encoding='utf-8') as f:
        f.write(soap_data)
    
    try:
        # SOAP zarfını parse et
        root = ET.fromstring(soap_data)
        
        # Namespace'leri tanımla
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://localhost/Intellect/ExternalWebService'
        }
        
        # İç XML verilerini çıkart
        request_data = root.find('.//ns:Request', namespaces)
        
        if request_data is not None:
            # HTML entity'lerini decode et (&lt; -> <, &gt; -> > vb.)
            inner_xml_encoded = request_data.text
            inner_xml = html.unescape(inner_xml_encoded)
            
            # İç XML'i parse et
            inner_root = ET.fromstring(inner_xml)
            
            # Anakart verilerini çıkart
            anakart_data = {}
            for child in inner_root:
                anakart_data[child.tag] = child.text
            
            # ID ve Key değerlerini al
            anakart_id = inner_root.get('ID')
            anakart_key = inner_root.get('Key')
            
            result = {
                'success': True,
                'anakart_id': anakart_id,
                'anakart_key': anakart_key,
                'anakart_data': anakart_data
            }
        else:
            result = {
                'success': False,
                'error': 'Request verisi bulunamadı'
            }
            
    except Exception as e:
        result = {
            'success': False,
            'error': str(e),
            'raw_data': soap_data
        }
    
    return jsonify(result)

@app.route('/', methods=['GET'])
def home():
    return """
    <html>
        <head>
            <title>SOAP Veri Alıcı</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>SOAP Veri Alıcı</h1>
            <p>Bu endpoint, SOAP XML verilerini almak için kullanılır.</p>
            <p>Örnek istek:</p>
            <pre>
POST /receive_soap HTTP/1.1
Content-Type: text/xml; charset=utf-8

&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soap:Body&gt;
        ...
    &lt;/soap:Body&gt;
&lt;/soap:Envelope&gt;
            </pre>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
