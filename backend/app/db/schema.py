import logging
from falkordb import FalkorDB

logger = logging.getLogger(__name__)

def init_schema(client: FalkorDB, graph_name: str = "case_shift"):
    """
    Initializes the FalkorDB schema for Tier 1 MVP.
    Creates necessary indexes for nodes to ensure fast lookups by durable IDs.
    """
    logger.info(f"Initializing schema for graph: {graph_name}")
    graph = client.select_graph(graph_name)

    # Tier 1 Node Labels and their durable IDs that need indexes
    indexes = [
        ("Case", "case_id"),
        ("DocketEntry", "entry_id"),
        ("Document", "doc_id"),
        ("Chunk", "chunk_id"),
        ("Party", "party_id"),     # For Party nodes
        ("Judge", "judge_id"),     # For Judge nodes
        ("EventType", "event_type_id"), # For EventType nodes
    ]

    for label, property_name in indexes:
        try:
            query = f"CREATE INDEX FOR (n:{label}) ON (n.{property_name})"
            graph.query(query)
            logger.info(f"Created index on {label}({property_name})")
        except Exception as e:
            # FalkorDB will raise an error if index already exists. We can safely ignore it.
            if "already exists" in str(e).lower() or "index already exists" in str(e).lower():
                logger.debug(f"Index on {label}({property_name}) already exists.")
            else:
                logger.warning(f"Error creating index on {label}({property_name}): {e}")

    logger.info("Schema initialization complete.")
