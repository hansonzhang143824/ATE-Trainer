"""Debug script for gen_paths trace"""
import sys
sys.path.insert(0, r"D:\Newtest\CLAUDE_PROCESS\Project\DALI")
import importlib.util
spec = importlib.util.spec_from_file_location("gen_paths", r"D:\Newtest\CLAUDE_PROCESS\Project\DALI\gen_paths.py")
gen_paths = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen_paths)

for src_port in ['S1_FPVIe_FH0', 'S1_FPVIe_SH0', 'S1_FPVIe_FL0', 'S1_FPVIe_SL0']:
    results = gen_paths.trace_single(src_port)
    print(f"{src_port}: {len(results)} paths")
    for dut, steps in results[:3]:
        relay_list = [(s['relay'], s['state'], s['rn']) for s in steps]
        print(f'  -> {dut}: {relay_list}')
    print()
