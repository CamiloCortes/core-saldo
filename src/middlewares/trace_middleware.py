import uuid
from fastapi import Request


async def trace_middleware(request: Request, call_next):
    incoming_trace_id = request.headers.get("x-trace-id")
    trace_id = incoming_trace_id or str(uuid.uuid4())

    request.state.trace_id = trace_id

    response = await call_next(request)

    response.headers["x-trace-id"] = trace_id

    return response
