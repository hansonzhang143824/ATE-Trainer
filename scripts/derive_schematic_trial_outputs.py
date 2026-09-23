#!/usr/bin/env python3
"""Retired PTC compatibility entrypoint."""
import sys
print('This JSON schematic projection is retired. Use the validated global TXT products; no trial JSON projection is allowed.', file=sys.stderr)
raise SystemExit(2)
