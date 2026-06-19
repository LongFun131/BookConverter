import chardet


FALLBACK_ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'latin-1']


def detect_encoding(raw_bytes: bytes) -> str:
    if not raw_bytes:
        return 'utf-8'
    result = chardet.detect(raw_bytes)
    return result.get('encoding') or 'utf-8'


def detect_and_decode(raw_bytes: bytes) -> str:
    if not raw_bytes:
        return ""
    encoding = detect_encoding(raw_bytes)
    try:
        return raw_bytes.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        pass
    for fallback in FALLBACK_ENCODINGS:
        try:
            return raw_bytes.decode(fallback)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw_bytes.decode('utf-8', errors='replace')


def ensure_utf8(text: str) -> bytes:
    return text.encode('utf-8')
