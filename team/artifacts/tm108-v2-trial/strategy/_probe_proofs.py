# read-only probe: compact per-terminal proof summary for the TM108 terminals (t4)
import io
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

P = pathlib.Path('team/artifacts/tm108-v2-trial/schematic/tm108-paths-proofs.json')
d = json.loads(P.read_text(encoding='utf-8'))
for pin, ps in d['proofs'].items():
    print('==== %s (%d accepted) ====' % (pin, len(ps)))
    for p in ps:
        sm = p.get('source_meta') or {}
        chain = ' -> '.join(
            '%s#%s(%s)' % (s['relay'], s['relay_number'], s['state']) for s in (p.get('path') or [])
        ) or '<EMPTY path>'
        print('  src=%-20s type=%-7s role=%-2s side=%-3s ch=%-2s dom=%-5s req=%-16s dut_net=%s'
              % (p['source_port'], sm.get('type', ''), sm.get('role') or '-', sm.get('side') or '-',
                 sm.get('channel') if sm.get('channel') not in (None, '') else '-',
                 sm.get('domain') or '-', str(p.get('required_on')), p.get('dut_net')))
        print('      %s' % chain)
    for r in d.get('rejected', {}).get(pin, []):
        print('  REJECTED src=%-20s net=%s reason=%s' % (r['source_port'], r['dut_net'], r['reason']))
