import logging

from django.db import connection

logger = logging.getLogger(__name__)


def check_database():
    """
    Return True if a trivial query succeeds against the default database.

    Any failure is logged (with traceback) and reported as False, so the
    caller never has to handle exceptions itself.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    except Exception:
        logger.exception("Health check: database query failed")
        return False