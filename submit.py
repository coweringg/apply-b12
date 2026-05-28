import os
import json
import hmac
import hashlib
import urllib.request
import datetime

def main():
    # Obtener la información desde variables de entorno
    name = os.environ.get("NAME")
    email = os.environ.get("EMAIL")
    resume_link = os.environ.get("RESUME_LINK")
    repository_link = os.environ.get("REPOSITORY_LINK")
    action_run_link = os.environ.get("ACTION_RUN_LINK")
    
    # La clave secreta debe tratarse como un secreto en la implementación
    signing_secret = os.environ.get("B12_SIGNING_SECRET")
    if not signing_secret:
        raise ValueError("Error: B12_SIGNING_SECRET environment variable is not set.")

    # Comprobar que todos los campos necesarios están presentes
    if not all([name, email, resume_link, repository_link, action_run_link]):
        raise ValueError("Faltan variables de entorno requeridas (NAME, EMAIL, RESUME_LINK, REPOSITORY_LINK, ACTION_RUN_LINK). Asegúrate de llenar los campos al ejecutar la acción.")

    # Formatear el timestamp en ISO 8601 (con milisegundos y 'Z' al final)
    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # Construir el payload (diccionario)
    payload = {
        "action_run_link": action_run_link,
        "email": email,
        "name": name,
        "repository_link": repository_link,
        "resume_link": resume_link,
        "timestamp": timestamp
    }

    # Serializar el JSON: sin espacios (compacto) y con las claves ordenadas alfabéticamente
    json_payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    encoded_payload = json_payload.encode('utf-8')

    # Calcular el HMAC-SHA256
    secret_bytes = signing_secret.encode('utf-8')
    signature = hmac.new(secret_bytes, encoded_payload, hashlib.sha256).hexdigest()

    # Configurar la petición POST
    url = "https://b12.io/apply/submission"
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": f"sha256={signature}"
    }

    req = urllib.request.Request(url, data=encoded_payload, headers=headers, method="POST")

    print(f"Enviando postulación para {name}...")
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_body = response.read().decode('utf-8')
                response_data = json.loads(response_body)
                if response_data.get("success"):
                    print("¡Éxito! Aquí tienes tu recibo:")
                    print("-" * 50)
                    print(response_data.get("receipt"))
                    print("-" * 50)
                else:
                    print("Respuesta 200 OK, pero el flag de 'success' no es verdadero.")
                    print(response_body)
            else:
                print(f"Código de estado inesperado: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"Error HTTP: {e.code}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
