from src.config import supabase

# Insert a Tweet mention
def insert_mention(tweet_id: int, replied_status: bool = False):
    data = {"id": tweet_id, "replied_status": replied_status}
    response = supabase.table("recluse_mentions").insert(data).execute()
    print(response)

# Example Usage
insert_mention(1623456789012345678)  # Replace with an actual tweet ID