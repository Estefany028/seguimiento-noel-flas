# services.py
import os
from datetime import datetime, date
from google_client import sheets_service

def _hoy_date():
    return date.today()

def _parse_sheet_date(val):
    if val in (None, ""):
        return None
    s = str(val).strip()
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    return None

def read_sheet_values(spreadsheet_id: str, range_a1: str):
    svc = sheets_service()
    resp = svc.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_a1,
        valueRenderOption="FORMATTED_VALUE"
    ).execute()
    return resp.get("values", [])

def write_sheet_value(spreadsheet_id: str, range_a1: str, value):
    svc = sheets_service()
    body = {"values": [[value]]}
    svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_a1,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

def obtener_personas_vigentes_externo():
    base_id = os.getenv("SPREADSHEET_BASE_ID")
    base_name = os.getenv("SHEET_BASE_NAME", "Base_Personas")

    if not base_id:
        raise RuntimeError("Falta SPREADSHEET_BASE_ID en .env")

    values = read_sheet_values(base_id, f"{base_name}!A1:AE")
    if not values:
        return []

    headers = values[0]
    rows = values[1:]

    def idx(name):
        try:
            return headers.index(name)
        except Exception:
            return -1

    idx_nombre = idx("NOMBRES")
    idx_apellido = idx("APELLIDOS")
    idx_empresa = idx("EMPRESA")
    idx_cedula = next((i for i, h in enumerate(headers) if "CEDUL" in str(h).upper()), -1)

    idx_fecha_fin = idx("FECHA FIN")
    if idx_fecha_fin == -1:
        idx_fecha_fin = 21  # fallback (col V)

    COL_CERT = 25  # Z (0-based)
    COL_IND  = 26  # AA
    COL_SS   = 29  # AD

    hoy = _hoy_date()
    out = []

    for r in rows:
        if idx_cedula < 0 or idx_cedula >= len(r) or not r[idx_cedula]:
            continue

        fin = _parse_sheet_date(r[idx_fecha_fin]) if idx_fecha_fin < len(r) else None
        if not fin or fin < hoy:
            continue

        certificados = r[COL_CERT] if COL_CERT < len(r) else ""
        induccion = r[COL_IND] if COL_IND < len(r) else ""
        seguridad = r[COL_SS] if COL_SS < len(r) else ""

        motivos = []
        if certificados != "CUMPLE":
            motivos.append("Certificados incompletos")
        if induccion != "VIGENTE":
            motivos.append("Inducción vencida o no registrada")
        if seguridad != "VIGENTE":
            motivos.append("Seguridad Social vencida")

        estado = "CUMPLE" if not motivos else "REVISAR"

        out.append({
            "nombre": f"{r[idx_nombre] if idx_nombre!=-1 else ''} {r[idx_apellido] if idx_apellido!=-1 else ''}".strip(),
            "cedula": r[idx_cedula],
            "empresa": r[idx_empresa] if idx_empresa!=-1 else "",
            "certificados": certificados,
            "induccion": induccion,
            "seguridadSocial": seguridad,
            "estado": estado,
            "motivo": " · ".join(motivos)
        })

    return out

def obtener_solicitudes_admin():
    base_id = os.getenv("SPREADSHEET_BASE_ID")
    base_name = os.getenv("SHEET_BASE_NAME", "Base_Personas")

    if not base_id:
        raise RuntimeError("Falta SPREADSHEET_BASE_ID en .env")

    values = read_sheet_values(base_id, f"{base_name}!A1:AE")
    if not values:
        return []

    headers = values[0]
    rows = values[1:]
    hoy = _hoy_date()

    def idx(name):
        try:
            return headers.index(name)
        except Exception:
            return -1

    idx_empresa = idx("EMPRESA")
    idx_nit = next((i for i, h in enumerate(headers) if "NIT" in str(h).upper()), -1)

    idx_hora_ing = idx("HORA INGRESO")
    idx_hora_sal = idx("HORA SALIDA")
    idx_tipo = idx("TIPO DE TRABAJO")
    idx_ext = idx("EXTENSION")
    idx_interv = idx("INTERVENTOR")
    idx_turno = idx("TURNO")
    idx_fini = idx("FECHA DE INICIO")
    idx_ffin = idx("FECHA FIN")
    if idx_ffin == -1:
        idx_ffin = 21

    idx_nombre = idx("NOMBRES")
    idx_apellido = idx("APELLIDOS")
    idx_cedula = next((i for i, h in enumerate(headers) if "CEDUL" in str(h).upper()), -1)

    idx_consec = idx("CONSECUTIVO")
    if idx_consec == -1:
        # Ajusta si tu consecutivo está en otra columna real
        idx_consec = 23

    COL_CERT = 25
    COL_IND  = 26
    COL_SS   = 29

    solicitudes = {}

    for sheet_row, r in enumerate(rows, start=2):
        if idx_cedula == -1 or idx_cedula >= len(r) or not r[idx_cedula]:
            continue

        fin = _parse_sheet_date(r[idx_ffin]) if idx_ffin < len(r) else None
        if not fin or fin < hoy:
            continue

        key = "|".join([
            str(r[idx_empresa]) if idx_empresa!=-1 else "",
            str(r[idx_nit]) if idx_nit!=-1 else "",
            str(r[idx_hora_ing]) if idx_hora_ing!=-1 else "",
            str(r[idx_hora_sal]) if idx_hora_sal!=-1 else "",
            str(r[idx_tipo]) if idx_tipo!=-1 else "",
            str(r[idx_ext]) if idx_ext!=-1 else "",
            str(r[idx_interv]) if idx_interv!=-1 else "",
            str(r[idx_turno]) if idx_turno!=-1 else "",
            str(r[idx_fini]) if idx_fini!=-1 else "",
            str(r[idx_ffin]) if idx_ffin!=-1 else "",
        ])

        if key not in solicitudes:
            solicitudes[key] = {
                "id": key,
                "empresa": r[idx_empresa] if idx_empresa!=-1 else "",
                "nit": r[idx_nit] if idx_nit!=-1 else "",
                "horaIngreso": r[idx_hora_ing] if idx_hora_ing!=-1 else "",
                "horaSalida": r[idx_hora_sal] if idx_hora_sal!=-1 else "",
                "tipoTrabajo": r[idx_tipo] if idx_tipo!=-1 else "",
                "extension": r[idx_ext] if idx_ext!=-1 else "",
                "interventor": r[idx_interv] if idx_interv!=-1 else "",
                "turno": r[idx_turno] if idx_turno!=-1 else "",
                "fechaInicio": r[idx_fini] if idx_fini!=-1 else "",
                "fechaFin": r[idx_ffin] if idx_ffin!=-1 else "",
                "personas": []
            }

        motivos = []
        if COL_CERT < len(r) and r[COL_CERT] != "CUMPLE": motivos.append("Certificados")
        if COL_IND < len(r) and r[COL_IND] != "VIGENTE": motivos.append("Inducción")
        if COL_SS < len(r) and r[COL_SS] != "VIGENTE": motivos.append("Seguridad Social")

        solicitudes[key]["personas"].append({
            "row": sheet_row,
            "nombre": f"{r[idx_nombre] if idx_nombre!=-1 else ''} {r[idx_apellido] if idx_apellido!=-1 else ''}".strip(),
            "cedula": r[idx_cedula],
            "estado": "CUMPLE" if not motivos else "REVISAR",
            "motivo": " · ".join(motivos),
            "consecutivo": r[idx_consec] if idx_consec < len(r) else ""
        })

    return list(solicitudes.values())

def actualizar_consecutivo(row: int, consecutivo: str):
    base_id = os.getenv("SPREADSHEET_BASE_ID")
    base_name = os.getenv("SHEET_BASE_NAME", "Base_Personas")

    if not base_id:
        raise RuntimeError("Falta SPREADSHEET_BASE_ID en .env")

    # Si tu consecutivo está en columna X:
    col_letter = "X"
    range_a1 = f"{base_name}!{col_letter}{row}"
    write_sheet_value(base_id, range_a1, consecutivo)
