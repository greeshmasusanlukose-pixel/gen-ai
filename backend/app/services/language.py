def resolve_language(text, requested='auto', fallback='ml'):
    if requested != 'auto':
        return requested
    if any('\u0d00' <= char <= '\u0d7f' for char in text):
        return 'ml'
    return 'en' if any(c.isascii() and c.isalpha() for c in text) else fallback
