"""Origin protection, bounded bodies, and security headers before routing."""
from starlette.responses import JSONResponse

from backend.app.core.errors import error_payload

SECURITY_HEADERS = {
    b"x-content-type-options": b"nosniff", b"x-frame-options": b"DENY",
    b"referrer-policy": b"same-origin", b"permissions-policy": b"camera=(), microphone=(), geolocation=()",
    b"cache-control": b"no-store",
}


class RequestProtectionMiddleware:
    def __init__(self, app, allowed_origins, production=False, body_limit=1024 * 1024, upload_body_limit=8 * 1024 * 1024):
        self.app = app
        self.allowed_origins = set(allowed_origins)
        self.production = production
        self.body_limit = body_limit
        self.upload_body_limit = upload_body_limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def safe_send(message):
            if message["type"] == "http.response.start":
                present = {key.lower() for key, _ in message.get("headers", [])}
                message["headers"] = list(message.get("headers", [])) + [(key, value) for key, value in SECURITY_HEADERS.items() if key not in present]
            await send(message)

        headers = {key.lower(): value for key, value in scope["headers"]}
        if scope["method"] in {"POST", "PATCH", "PUT", "DELETE"}:
            origin = headers.get(b"origin", b"").decode("latin1")
            if self.production and b"cookie" in headers and not origin:
                return await JSONResponse(error_payload("ORIGIN_REQUIRED","Authenticated production mutations require an allowed Origin."),status_code=403)(scope,receive,safe_send)
            if origin and origin not in self.allowed_origins:
                return await JSONResponse(error_payload("ORIGIN_REJECTED", "Request origin is not allowed."), status_code=403)(scope, receive, safe_send)
            limit = self.upload_body_limit if "/imports/" in scope["path"] or scope["path"].endswith("/attachments") else self.body_limit
            try:
                too_large = int(headers.get(b"content-length", b"0")) > limit
            except ValueError:
                too_large = False
            if too_large:
                return await JSONResponse(error_payload("BODY_TOO_LARGE", "Request body is too large."), status_code=413)(scope, receive, safe_send)
            chunks, size = [], 0
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                chunk = message.get("body", b"")
                size += len(chunk)
                if size > limit:
                    return await JSONResponse(error_payload("BODY_TOO_LARGE", "Request body is too large."), status_code=413)(scope, receive, safe_send)
                chunks.append(chunk)
                if not message.get("more_body", False):
                    break
            body, consumed = b"".join(chunks), False

            async def replay():
                nonlocal consumed
                if not consumed:
                    consumed = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return await receive()
            return await self.app(scope, replay, safe_send)
        return await self.app(scope, receive, safe_send)


class StructuredRequestLoggingMiddleware:
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        if scope['type']!='http':return await self.app(scope,receive,send)
        import json,logging,re,time
        from uuid import uuid4
        supplied=dict(scope['headers']).get(b'x-request-id',b'').decode('latin1')
        request_id=supplied if re.fullmatch(r'[A-Za-z0-9_-]{1,64}',supplied) else str(uuid4())
        status=500;started=time.perf_counter()
        async def observed_send(message):
            nonlocal status
            if message['type']=='http.response.start':
                status=message['status'];message['headers']=list(message.get('headers',[]))+[(b'x-request-id',request_id.encode())]
            await send(message)
        try:await self.app(scope,receive,observed_send)
        finally:
            route=getattr(scope.get('route'),'path','unknown_route')
            logging.getLogger('pravaha.requests').info(json.dumps({'requestId':request_id,'method':scope['method'],'route':route,'status':status,'durationMs':round((time.perf_counter()-started)*1000,2),'role':scope.get('state',{}).get('role'),'errorCategory':'server' if status>=500 else 'request' if status>=400 else None}))
