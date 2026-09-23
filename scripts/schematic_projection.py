#!/usr/bin/env python3
"""Read a verified lossless schematic JSON projection as exact source text."""
from __future__ import annotations
import base64, hashlib, json
from pathlib import Path

def read_schematic_text(path: str | Path) -> str:
    path=Path(path); raw=path.read_bytes()
    try:
        data=json.loads(raw.decode('utf-8-sig'))
    except (UnicodeDecodeError,json.JSONDecodeError):
        for encoding in ('utf-8-sig','utf-8','gbk','latin-1'):
            try: return raw.decode(encoding)
            except UnicodeDecodeError: continue
        return raw.decode('utf-8',errors='replace')
    if data.get('format') != 'lossless-text-projection':
        return raw.decode('utf-8-sig')
    projected=base64.b64decode(data.get('rawBytesBase64',''),validate=True)
    source=data.get('sourceTxt',{})
    if source.get('sha256') != hashlib.sha256(projected).hexdigest():
        raise ValueError(f'{path}: lossless JSON sourceTxt hash mismatch')
    return projected.decode(source.get('encoding','utf-8'))
