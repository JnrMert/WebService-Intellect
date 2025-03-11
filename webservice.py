from flask import Flask, request, Response

app = Flask(__name__)

# 📌 GET isteği ile gelen SOAP XML'i yakala ve ekrana yazdır
@app.route("/", methods=["GET"])
def receive_soap_request():
    xml_data = request.data.decode("utf-8")  # Gelen XML verisini al

    if not xml_data:
        return Response("Boş XML geldi!", mimetype="text/plain", status=400)

    print("\n📥 Gelen SOAP XML:\n", xml_data)  # Gelen XML içeriğini konsola yazdır

    return Response("XML alındı!", mimetype="text/plain", status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
