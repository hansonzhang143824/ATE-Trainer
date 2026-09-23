#!/usr/bin/env python3
"""Retired PTC compatibility entrypoint."""
import sys
print('This JSON schematic generator is retired. Run scripts/generate_schematic_txt.py; complete TXT products are required.', file=sys.stderr)
raise SystemExit(2)
