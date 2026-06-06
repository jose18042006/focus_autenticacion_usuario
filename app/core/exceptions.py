import logging
from litestar import Request, Response
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("GlobalExceptionHandler")

def internal_server_error_handler(request: Request, exc: Exception) -> Response:
    
    logger.error(
        f"Big error on {request.method} {request.url.path} | Detail: {str(exc)}", 
        exc_info=exc
    )

    return Response(
        content={
            "error": "InternalServerError",
            "detail": "Unexpected error in internal server.",
            "path": request.url.path
        },
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )

def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    logger.warning(f"Excepción HTTP {exc.status_code} at {request.url.path}: {exc.detail}")
    
    return Response(
        content={
            "error": exc.__class__.__name__,
            "detail": exc.detail,
            "path": request.url.path
        },
        status_code=exc.status_code,
    )

GLOBAL_EXCEPTION_HANDLERS = {
    Exception: internal_server_error_handler,
    HTTPException: http_exception_handler,
}