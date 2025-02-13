from src.config import supabase

response = supabase.table("recluse_mentions").select("*").execute()
print(response)