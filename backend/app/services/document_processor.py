"""Bounded file validation and provider boundaries; uploaded content is never executed."""
import base64,hashlib,io,re,warnings,wave,zipfile
from pathlib import PurePosixPath
from typing import Protocol
from PIL import Image
from backend.app.core.errors import ApiError

DEFAULT_MAX_BYTES=5*1024*1024
DEFAULT_IMAGE_MAX_PIXELS=20_000_000

class OCRProvider(Protocol):
    def extract(self, content: bytes, mime_type: str) -> dict: ...

class ASRProvider(Protocol):
    def transcribe(self, content: bytes, mime_type: str) -> dict: ...

class AdvancedIntelligenceProvider(Protocol):
    def rank(self, text: str, candidates: list[dict]) -> dict: ...


def safe_filename(value):
    name=PurePosixPath(value.replace("\\","/")).name
    name=re.sub(r'[^A-Za-z0-9._ -]','_',name).strip('. ')
    if not name or len(name)>255:raise ApiError(400,"INVALID_FILE","Filename is invalid.")
    return name


def decode_file(body, settings=None):
    max_bytes = getattr(settings, "attachment_max_bytes", DEFAULT_MAX_BYTES)
    image_max_pixels = getattr(settings, "image_max_pixels", DEFAULT_IMAGE_MAX_PIXELS)
    xlsx_max_entries = getattr(settings, "xlsx_max_entries", 1000)
    xlsx_max_uncompressed_bytes = getattr(settings, "xlsx_max_uncompressed_bytes", 40 * 1024 * 1024)
    xlsx_max_compression_ratio = getattr(settings, "xlsx_max_compression_ratio", 300)
    try:content=base64.b64decode(body.contentBase64,validate=True)
    except (ValueError,TypeError):raise ApiError(400,"INVALID_FILE","File encoding is invalid.") from None
    size_label = f"{max_bytes // (1024 * 1024)} MiB" if max_bytes % (1024 * 1024) == 0 else f"{max_bytes} bytes"
    if not content or len(content)>max_bytes:raise ApiError(413,"FILE_TOO_LARGE",f"File must contain 1 byte to {size_label}.")
    filename=safe_filename(body.filename)
    suffix=PurePosixPath(filename).suffix.lower()
    try:
        if suffix in {".csv",".txt"}:
            content.decode("utf-8-sig")
            if b"\x00" in content:raise ValueError()
            mime="text/csv" if suffix==".csv" else "text/plain"
        elif suffix==".xlsx":
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                entries=z.infolist()
                if len(entries)>xlsx_max_entries or sum(i.file_size for i in entries)>xlsx_max_uncompressed_bytes or any(i.file_size/max(1,i.compress_size)>xlsx_max_compression_ratio for i in entries):raise ValueError()
                names={i.filename for i in entries}
                if '[Content_Types].xml' not in names or 'xl/workbook.xml' not in names or any('vbaProject' in n or 'externalLinks/' in n for n in names):raise ValueError()
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif suffix in {".png",".jpg",".jpeg"}:
            Image.MAX_IMAGE_PIXELS = image_max_pixels
            with warnings.catch_warnings():
                warnings.simplefilter("error",Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(content)) as image:
                    expected="PNG" if suffix==".png" else "JPEG"
                    if image.format!=expected:raise ValueError()
                    image.verify()
            mime="image/png" if suffix==".png" else "image/jpeg"
        elif suffix==".pdf":
            if not content.startswith(b'%PDF-') or b'%%EOF' not in content[-1024:]:raise ValueError()
            if any(token in content for token in [b'/JavaScript',b'/Launch',b'/EmbeddedFile',b'/OpenAction']):raise ValueError()
            mime="application/pdf"
        elif suffix==".wav":
            with wave.open(io.BytesIO(content)) as audio:
                if audio.getnchannels() not in {1,2} or not 8000<=audio.getframerate()<=96000 or audio.getnframes()/audio.getframerate()>300:raise ValueError()
            mime="audio/wav"
        else:raise ValueError()
    except Exception:
        raise ApiError(400,"INVALID_FILE","Unsupported, unsafe, oversized archive or invalid file content. Supported: CSV/XLSX/TXT/PDF/PNG/JPEG/WAV.") from None
    return {"filename":filename,"content":content,"mimeType":mime,"size":len(content),"checksum":hashlib.sha256(content).hexdigest()}


def provider_result(kind, configured):
    # No remote providers are implemented/configured: never fabricate extraction.
    return {"provider":kind,"status":"NOT_CONFIGURED" if configured in {"","none"} else "UNAVAILABLE",
        "text":None,"reason":"No executable provider is installed. Deterministic text matching remains available; PM approval is required."}
