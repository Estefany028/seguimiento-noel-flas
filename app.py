import ssl
import requests
import urllib3

# 1) Ignorar verificación SSL global (algunas libs lo respetan, otras no)
ssl._create_default_https_context = ssl._create_unverified_context

# 2) Forzar verify=False en TODAS las requests
_original_request = requests.Session.request

def _patched_request(self, method, url, **kwargs):
    kwargs["verify"] = False
    return _original_request(self, method, url, **kwargs)

requests.Session.request = _patched_request

# 3) Quitar warnings de "InsecureRequestWarning"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from flask import Flask, render_template, request, jsonify, abort
from dotenv import load_dotenv

from services import (
    obtener_personas_vigentes_externo,
    obtener_solicitudes_admin,
    actualizar_consecutivo
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

def is_admin_request():
    # MVP: token simple
    token = request.headers.get("X-ADMIN-TOKEN") or request.args.get("admin_token")
    return token and token == os.getenv("ADMIN_TOKEN")

@app.get("/")
def home():
    # Un solo link. La vista decide en el front si es admin, probando endpoint admin.
    return render_template("index.html")

@app.get("/api/external")
def api_external():
    data = obtener_personas_vigentes_externo()
    return jsonify(data)

@app.get("/api/admin/solicitudes")
def api_admin_solicitudes():
    if not is_admin_request():
        abort(403)
    data = obtener_solicitudes_admin()
    return jsonify(data)

@app.post("/api/admin/consecutivo")
def api_admin_consecutivo():
    if not is_admin_request():
        abort(403)

    payload = request.get_json(force=True)
    row = int(payload["row"])
    consecutivo = str(payload["consecutivo"]).strip()

    if not consecutivo:
        return jsonify({"ok": False, "error": "Consecutivo vacío"}), 400

    actualizar_consecutivo(row=row, consecutivo=consecutivo)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)


import ssl
import requests
import urllib3

# 1) Ignorar verificación SSL global (algunas libs lo respetan, otras no)
ssl._create_default_https_context = ssl._create_unverified_context

# 2) Forzar verify=False en TODAS las requests
_original_request = requests.Session.request

def _patched_request(self, method, url, **kwargs):
    kwargs["verify"] = False
    return _original_request(self, method, url, **kwargs)

requests.Session.request = _patched_request

# 3) Quitar warnings de "InsecureRequestWarning"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from flask import Flask, render_template, request, jsonify, abort
from dotenv import load_dotenv

from services import (
    obtener_personas_vigentes_externo,
    obtener_solicitudes_admin,
    actualizar_consecutivo
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

def is_admin_request():
    # MVP: token simple
    token = request.headers.get("X-ADMIN-TOKEN") or request.args.get("admin_token")
    return token and token == os.getenv("ADMIN_TOKEN")

@app.get("/")
def home():
    # Un solo link. La vista decide en el front si es admin, probando endpoint admin.
    return render_template("index.html")

@app.get("/api/external")
def api_external():
    data = obtener_personas_vigentes_externo()
    return jsonify(data)

@app.get("/api/admin/solicitudes")
def api_admin_solicitudes():
    if not is_admin_request():
        abort(403)
    data = obtener_solicitudes_admin()
    return jsonify(data)

@app.post("/api/admin/consecutivo")
def api_admin_consecutivo():
    if not is_admin_request():
        abort(403)

    payload = request.get_json(force=True)
    row = int(payload["row"])
    consecutivo = str(payload["consecutivo"]).strip()

    if not consecutivo:
        return jsonify({"ok": False, "error": "Consecutivo vacío"}), 400

    actualizar_consecutivo(row=row, consecutivo=consecutivo)
    return jsonify({"ok": True})

    
@app.get("/api/whoami")
def whoami():
    import json
    with open("service_account.json", "r", encoding="utf-8") as f:
        info = json.load(f)
    return {"service_account": info.get("client_email")}

if __name__ == "__main__":
    app.run(debug=True)


