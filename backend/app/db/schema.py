import logging
from falkordb import FalkorDB

logger = logging.getLogger(__name__)


def init_schema(client: FalkorDB, graph_name: str = "case_shift"):
    """
    Initializes the FalkorDB schema for Tier 1 MVP.
    Creates indexes needed for durable-ID lookup and core Tier 1 retrieval paths.
    """
    logger.info(f"Initializing schema for graph: {graph_name}")
    graph = client.select_graph(graph_name)

    # Required Tier 1 indexes for durable IDs and common retrieval paths.
    indexes = [
        ("Case", "case_id"),
        ("DocketEntry", "entry_id"),
        ("DocketEntry", "case_id"),
        ("DocketEntry", "filed_at"),
        ("Document", "doc_id"),
        ("Document", "case_id"),
        ("Document", "entry_id"),
        ("Document", "filed_at"),
        ("Chunk", "chunk_id"),
        ("Chunk", "doc_id"),
        ("Chunk", "case_id"),
        ("Party", "party_id"),
        ("Judge", "judge_id"),
        ("EventType", "event_type_id"),
    ]

    failures = []

    for label, property_name in indexes:
        try:
            query = f"CREATE INDEX FOR (n:{label}) ON (n.{property_name})"
            graph.query(query)
            logger.info(f"Created index on {label}({property_name})")
        except Exception as e:
            if "already exists" in str(e).lower() or "index already exists" in str(e).lower():
                logger.debug(f"Index on {label}({property_name}) already exists.")
            else:
                logger.warning(f"Error creating index on {label}({property_name}): {e}")
                failures.append(e)

    if failures:
        raise RuntimeError(f"Failed to create {len(failures)} index(es). First error: {failures[0]}")

    logger.info("Schema initialization complete.")
