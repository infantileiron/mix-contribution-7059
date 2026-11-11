import hashlib
import json


def checksum(rows) -> str:
    """与分解结果 checksum 完全一致的观测行指纹。"""
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
