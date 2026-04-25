import logging
import sys
from urllib.parse import urlsplit

from falkordb import FalkorDB

from app.core.config import settings
from app.db.schema import init_schema

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _redact_url(url: str) -> str:
    parts = urlsplit(url)
    host = parts.hostname or "unknown-host"
    if parts.port:
        host = f"{host}:{parts.port}"
    return f"{parts.scheme}://{host}{parts.path}"


def main():
    logger.info(
        "Connecting to FalkorDB at %s for graph %s",
        _redact_url(settings.falkordb_url),
        settings.falkordb_graph_name,
    )

    try:
        client = FalkorDB.from_url(settings.falkordb_url)
        init_schema(client, settings.falkordb_graph_name)
        logger.info("Successfully initialized FalkorDB schema.")
    except Exception:
        logger.exception("Failed to initialize schema")
        sys.exit(1)


if __name__ == "__main__":
    main()
