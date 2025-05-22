from bson import ObjectId


def sanitize_mongo_document(doc):
    if isinstance(doc, dict):
        return {
            k: sanitize_mongo_document(v)
            for k, v in doc.items()
            if v is not None  # skip nulls if needed
        }
    elif isinstance(doc, list):
        return [sanitize_mongo_document(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc
