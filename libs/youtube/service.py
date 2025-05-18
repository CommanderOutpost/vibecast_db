from fastapi import HTTPException, status
from bson import ObjectId
from libs.database.youtube.channels import get_channel_by_id


async def get_channel_info(channel_id: str) -> dict:
    """
    Fetch the full channel document from Mongo by its _id,
    convert ObjectId → str, and return everything else intact.
    """
    # validate the ID
    try:
        ObjectId(channel_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid channel_id {channel_id!r}",
        )

    doc = await get_channel_by_id(channel_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_id!r} not found",
        )

    # convert _id → id
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)

    return doc
