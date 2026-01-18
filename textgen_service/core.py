import os
import logging
import pandas as pd
from typing import List, Any, Optional

try:
    from langchain_community.vectorstores import FAISS
    from langchain.docstore.document import Document
except Exception:
    FAISS = Any
    Document = Any


logger = logging.getLogger("cyberguard.core")

USEFUL_COLUMNS: List[str] = [
    "attack_type",
    "attack_severity",
    "data_exfiltrated",
    "threat_intelligence",
    "response_action",
    "user_agent"
]


def ingest_cybersecurity_csv(
    csv_path: str,
    vector_store_path: str,
    embedding_model: Any
) -> Any:

    logger.info(f"Ingesting CSV: {csv_path}")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    df = pd.read_csv(csv_path)
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    documents: List[Any] = []

    for _, row in df.iterrows():

        parts: List[str] = ["A cybersecurity event was recorded."]

        for col in USEFUL_COLUMNS:
            if col in df.columns and pd.notna(row[col]):
                parts.append(f"{col.replace('_',' ').title()}: {row[col]}.")

        documents.append(
            Document(
                page_content=" ".join(parts),
                metadata={
                    "source_csv": os.path.basename(csv_path),
                    "event_id": row.get("event_id", "N/A"),
                    "timestamp": row.get("timestamp", "N/A")
                }
            )
        )

    if not documents:
        raise ValueError("No documents created")

    db = FAISS.from_documents(documents, embedding_model)

    os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)
    db.save_local(vector_store_path)

    logger.info("Vectorstore created successfully")

    return db


def choose_n_gpu_layers(env_flag: Optional[str]) -> int:
    """
    HF Spaces CPU = 0
    GPU space = -1
    """
    if env_flag and env_flag.lower() in ("1", "true", "yes"):
        return -1
    return 0
