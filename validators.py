import re
from io import BytesIO
from pypdf import PdfReader
from googleapiclient.http import MediaIoBaseDownload

PATRONES_FECHA_PAGO = [
    re.compile(r"PAGADO[\s\S]{0,120}(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})", re.I),
    re.compile(r"PAGADA[\s\S]{0,120}(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})", re.I),
    re.compile(r"FECHA\s*DE\s*PAGO[\s\S]{0,120}(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})", re.I),
    re.compile(r"Fecha\s*Pago[\s\S]{0,120}(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})", re.I),
]

def extraer_file_id(url: str) -> str | None:
    if not url:
        return None
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url) or re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    return m.group(1) if m else None

def leer_texto_pdf_desde_drive(drive, file_id: str) -> str:
    request = drive.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.seek(0)
    reader = PdfReader(fh)
    textos = []
    for page in reader.pages:
        textos.append(page.extract_text() or "")
    return " ".join(textos).replace("\n", " ")

def extraer_fecha_pago_desde_pdf_texto(texto: str) -> str | None:
    if not texto:
        return None
    texto = re.sub(r"\s+", " ", texto)
    for p in PATRONES_FECHA_PAGO:
        m = p.search(texto)
        if m and m.group(1):
            return m.group(1)
    return None
