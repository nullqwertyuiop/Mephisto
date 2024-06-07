from hashlib import sha256
from typing import IO


def sha256_hash(data: IO[bytes], chunk_size: int = 4096) -> str:
    result = sha256()
    for chunk in iter(lambda: data.read(chunk_size), b""):
        result.update(chunk)
    return result.hexdigest()
