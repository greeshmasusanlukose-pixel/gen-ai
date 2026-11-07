from io import BytesIO
from pathlib import Path
import warnings
import wave
from PIL import Image
from pypdf import PdfReader
from app.core.exceptions import AppError
from app.core.security import reject_secrets
from app.services.ai_service import require_capability

async def process_upload(upload, language, settings, provider):
    data = await upload.read(settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
    await upload.close()
    if not data or len(data) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise AppError(413, 'file_size', 'File is empty or exceeds upload limit')
    suffix = Path(upload.filename or '').suffix.lower()
    try:
        if suffix in {'.png', '.jpg', '.jpeg', '.webp'}:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(BytesIO(data)) as image:
                    if image.width * image.height > 16000000:
                        raise ValueError('image too large')
                    media = Image.MIME.get(image.format)
                    expected = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}
                    if media != expected[suffix]:
                        raise ValueError('format mismatch')
                    image.verify()
            operation, text = 'image', None
        elif suffix == '.txt':
            text = data.decode('utf-8')
            if '\x00' in text or not text.strip():
                raise ValueError('invalid text')
            media, operation = 'text/plain', 'document'
        elif suffix == '.pdf':
            if not data.startswith(b'%PDF-'):
                raise ValueError('invalid pdf')
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted or len(reader.pages) > 30:
                raise ValueError('encrypted or too many pages')
            text = '\n'.join(page.extract_text() or '' for page in reader.pages)
            if not text.strip():
                raise ValueError('scanned PDF requires OCR')
            media, operation = 'application/pdf', 'document'
        elif suffix == '.wav':
            with wave.open(BytesIO(data)) as audio:
                if audio.getnframes() / audio.getframerate() > 120:
                    raise ValueError('audio too long')
            media, operation, text = 'audio/wav', 'transcribe', None
        else:
            raise AppError(415, 'unsupported_file', 'Supported files: PNG, JPEG, WebP, UTF-8 TXT, text PDF, PCM WAV')
        if text is not None:
            if len(text) > 50000:
                raise ValueError('document too long')
            reject_secrets(text)
    except AppError:
        raise
    except Exception:
        raise AppError(422, 'invalid_file', 'File content is invalid or exceeds processing limits') from None
    require_capability(provider, operation)
    if operation == 'document':
        result = await provider.document(text, language)
    elif operation == 'image':
        result = await provider.image(data, media, language)
    else:
        result = await provider.transcribe(data, media, language)
    reject_secrets(result.text)
    for step in result.steps:
        reject_secrets(step)
    # Only metadata is persisted. Raw documents/images/audio may contain unseen secrets.
    return media, len(data), result
