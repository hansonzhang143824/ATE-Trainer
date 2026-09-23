# -*- coding: utf-8 -*-
"""One-shot reproducible producer for dft-ir.json: build (part1+part2) then apply the follow-up patches.

Usage:  python dft_ir_generate.py
Writes: team/artifacts/<run-id>/dft-ir.json
"""
import os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

runpy.run_path(os.path.join(HERE, 'dft_ir_build.py'), run_name='__main__')
runpy.run_path(os.path.join(HERE, 'dft_ir_patch_captain_requirements.py'), run_name='__main__')
runpy.run_path(os.path.join(HERE, 'dft_ir_patch_implementer_review.py'), run_name='__main__')
runpy.run_path(os.path.join(HERE, 'dft_ir_patch_rulings.py'), run_name='__main__')
runpy.run_path(os.path.join(HERE, 'dft_ir_patch_captain4_rulings.py'), run_name='__main__')
