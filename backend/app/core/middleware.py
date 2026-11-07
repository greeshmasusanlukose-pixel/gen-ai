from starlette.responses import JSONResponse

class BodyLimit:
    """Bound even chunked request bodies before multipart parsing/spooling."""
    def __init__(self, app, limit):
        self.app, self.limit = app, limit
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            size += len(message.get('body', b''))
            if size > self.limit:
                return await JSONResponse({'error': {'code': 'request_too_large', 'message': 'Request exceeds size limit'}}, status_code=413)(scope, receive, send)
            chunks.append(message)
            if not message.get('more_body', False):
                break
        index = 0
        async def replay():
            nonlocal index
            if index < len(chunks):
                result = chunks[index]
                index += 1
                return result
            return await receive()
        await self.app(scope, replay, send)
