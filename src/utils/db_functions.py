from sqlalchemy.orm import Session
from models import Mention  # Assuming there is a Mention model defined

def check_mentions_replied(db: Session, mentions: list) -> list:
    """
    Checks if each mention in the provided list has been replied to by querying the database.

    Args:
        db (Session): The database session.
        mentions (list): A list of mention IDs to check.

    Returns:
        list: A list of booleans indicating whether each mention has been replied to.
    """
    replied_status = []
    for mention_id in mentions:
        mention = db.query(Mention).filter(Mention.id == mention_id).first()
        replied_status.append(mention.replied if mention else False)
    return replied_status

def mark_mention_as_replied(db: Session, mention_id: int) -> None:
    """
    Mark a mention as replied to in the database.

    Args:
        db (Session): The database session.
        mention_id (int): The ID of the mention to mark.

    Returns:
        None
    """
    mention = db.query(Mention).filter(Mention.id == mention_id).first()
    if mention:
        mention.replied = True
        db.commit()
