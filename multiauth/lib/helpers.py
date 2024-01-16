import hashlib
import random
import string


def generate_seeded_slug(input_string: str, slug_length: int = 10) -> str:
    # Hash the input string
    hasher = hashlib.sha256()
    hasher.update(input_string.encode('utf-8'))
    hash_digest = hasher.digest()

    # Seed the random number generator
    seed = int.from_bytes(hash_digest, 'big')
    random.seed(seed)

    # Generate the slug
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(slug_length))
