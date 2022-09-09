import api.logging

logger = api.logging.get_logger(__name__)


def healthcheck_get():
    logger.info("GET /v1/healthcheck")
    return True, 200
