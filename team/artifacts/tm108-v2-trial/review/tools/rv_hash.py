import sys, hashlib, os, json

def info(p):
    with open(p, 'rb') as f:
        b = f.read()
    h = hashlib.sha256(b).hexdigest()
    bom = b[:3] == b'\xef\xbb\xbf'
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n')
    lone_lf = lf - crlf
    return {
        'path': p,
        'bytes': len(b),
        'sha256_plaintext': h,
        'utf8_bom': bom,
        'crlf': crlf,
        'lf_total': lf,
        'lone_lf': lone_lf,
        'header_hex': b[:8].hex(),
    }

if __name__ == '__main__':
    out = [info(p) for p in sys.argv[1:]]
    print(json.dumps(out, indent=2, ensure_ascii=False))
