from flask import Flask, request, Response

app = Flask(__name__)

# 📌 Gelen GET isteğini logla
@app.route("/", methods=["GET"])
def receive_soap_request():
    print("\n==> Yeni GET isteği alındı!")
    
    # 📌 Tüm başlıkları yazdır
    print("📌 Başlıklar:", request.headers)

    # 📌 XML içeriği varsa yazdır
    xml_data = request.data.decode("utf-8")  # Gelen XML verisini al

    if xml_data:
        print("\n📥 Gelen SOAP XML:\n", xml_data)
    else:
        print("\n⚠️ Uyarı: Gelen istekte XML verisi YOK!")

    return Response("GET isteği alındı, logları kontrol et!", mimetype="text/plain", status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
