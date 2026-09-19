from hashids import Hashids
from django.conf import settings

# SECRET_KEY as the salt means IDs are only decodable by your app instance
hashids = Hashids(salt=settings.SECRET_KEY, min_length=6)

def encode_id(pk: int) -> str:
    return hashids.encode(pk)

def decode_id(hash_str: str) -> int | None:
    decoded = hashids.decode(hash_str)
    return decoded[0] if decoded else None