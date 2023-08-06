from typing import Tuple, List

from firebase_admin import firestore


def get_site_key(site_key:str) -> dict:
    db = firestore.client()
    doc = db.document(f"siteKeys/{site_key}").get()
    if doc.exists is False:
        raise ValueError(f"Site key {site_key} does not exist")
    return doc.to_dict()


def query_all_site_keys() -> List[Tuple[str, dict]]:
    db = firestore.client()
    docs = db.collection("siteKeys").get()
    return [(doc.id, doc.to_dict()) for doc in docs]

