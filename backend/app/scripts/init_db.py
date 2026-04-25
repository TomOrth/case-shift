import logging
from falkordb import FalkorDB
from app.core.config import settings
from app.db.schema import init_schema

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info(f"Connecting to FalkorDB at {settings.falkordb_url}")

    try:
        # FalkorDB.from_url typically parses redis:// URLs
        # In the python falkordb package, the typical initialization is:
        # db = FalkorDB(host='...', port=...)
        # We can use from_url since falkordb wraps redis
        client = FalkorDB.from_url(settings.falkordb_url)
        init_schema(client)
        logger.info("Successfully initialized FalkorDB schema.")
    except Exception as e:
        logger.error(f"Failed to initialize schema: {e}")

if __name__ == "__main__":
    main()
