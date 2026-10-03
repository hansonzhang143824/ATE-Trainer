#!/usr/bin/env python3
"""Run original schematic engines against an explicitly frozen training run.

The old production entry points are intentionally unchanged. Their parser also
uses Pin_Channel_define.h: obtain that dependency from the host snapshot manifest,
never by following the production paths in the copied project configuration.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, io, json, os, re, secrets, shutil, stat, subprocess, sys
from pathlib import Path
import dft_source
from material_plaintext_hash import sha256_plaintext

ROOT = Path(__file__).resolve().parent.parent
NAMES = ('SCH-Connect-Map.txt', 'SCH-Connect-Map.json', 'Component-Statistic.txt',
         'Components-Statistic.json', 'Path-Proofs.txt', 'Path-Proofs.json', 'schematic-receipt.json')


def secure_path(value, boundary, require_file=False):
    candidate = Path(value).absolute()
    if '..' in candidate.parts:
        raise ValueError('training paths cannot contain parent traversal')
    for entry in (candidate, *candidate.parents):
        try:
            info = entry.lstat()
        except FileNotFoundError:
            continue
        if entry.is_symlink() or getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024):
            raise ValueError(f'training paths cannot contain links or junctions: {entry}')
        if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
            raise ValueError(f'training file cannot be hardlinked: {entry}')
    candidate = candidate.resolve()
    if not candidate.is_relative_to(Path(boundary).resolve()):
        raise ValueError(f'training path escapes its run boundary: {candidate}')
    if require_file and not candidate.is_file():
        raise FileNotFoundError(candidate)
    return candidate


def training_layout(input_root, out_dir, run_root, source, confirmed, cbit):
    if any(value is None for value in (input_root, out_dir, run_root, source, confirmed, cbit)):
        raise ValueError('all explicit training path arguments are required together')
    runs = (ROOT / 'Training_Materials' / 'runs').resolve()
    run = secure_path(run_root, runs)
    if (run.parent != runs or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}', run.name)
            or run.name.endswith('.') or re.match(r'(?i)^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)', run.name)):
        raise ValueError('run-root must name one Training_Materials/runs/<runId> directory')
    inputs = secure_path(input_root, run)
    out = secure_path(out_dir, run)
    if inputs != run / 'input' or out != run / 'input-sync' / 'schematic':
        raise ValueError('training paths must use run/input and run/input-sync/schematic')
    approved = [secure_path(value, inputs, True) for value in (source, confirmed, cbit)]
    if len(set(approved)) != 3:
        raise ValueError('schematic, confirmation and CBIT must be distinct input files')
    # The original validator owns this canonical name; do not replace its input
    # resolution or relax the original three-source receipt contract.
    if approved[2] != inputs / 'CBIT表-DALI.xlsx':
        raise ValueError('training CBIT snapshot must use the original validator name CBIT表-DALI.xlsx')
    for name in NAMES:
        secure_path(out / name, out)
    return run, inputs, out, *approved


def load_dependencies(run, source, confirmed, cbit):
    manifest_file = secure_path(run / 'pipeline-material-manifest.json', run, True)
    manifest = json.loads(manifest_file.read_text(encoding='utf-8-sig'))
    if (manifest.get('schemaVersion') != 1 or manifest.get('kind') != 'ptc-pipeline-materials' or manifest.get('runId') != run.name
            or not re.fullmatch(r'[a-f0-9]{64}', manifest.get('pipelineCacheKey', ''))):
        raise ValueError('pipeline material manifest identity differs')
    address = manifest.get('addressBook', {})
    files = manifest.get('files', [])

    def snapshot(relative):
        if not isinstance(relative, str) or not relative:
            raise ValueError('required parser dependency is not snapshotted')
        entries = [entry for entry in files if entry.get('snapshotPath') == relative]
        if len(entries) != 1:
            raise ValueError(f'parser dependency has no unique snapshot receipt: {relative}')
        entry = entries[0]
        actual = entry.get('baselinePath') if entry.get('mutable') else relative
        if not isinstance(actual, str) or not actual:
            raise ValueError('mutable parser dependency lacks an immutable baseline')
        file = secure_path(ROOT / actual, run / 'vs-baseline' if entry.get('mutable') else run, True)
        if (entry.get('view') != 'python-plaintext'
                or not re.fullmatch(r'[a-f0-9]{64}', entry.get('sha256', ''))
                or sha256_plaintext(file) != entries[0]['sha256']):
            raise ValueError(f'parser dependency snapshot hash differs: {relative}')
        return file

    for key, expected in [('schematic', source), ('confirmed', confirmed), ('cbit', cbit)]:
        if snapshot(address.get('input', {}).get(key)) != expected:
            raise ValueError(f'explicit {key} differs from the pipeline snapshot')
    config_file = snapshot(address.get('originalProjectConfigPath'))
    original_config = json.loads(config_file.read_text(encoding='utf-8-sig'))
    channelmap_source = original_config.get('inputs', {}).get('channelmap')
    if not isinstance(channelmap_source, str) or not channelmap_source:
        raise ValueError('original project configuration has no channelmap dependency')
    original_config_entries = [entry for entry in files if entry.get('snapshotPath') == address['originalProjectConfigPath']]
    config_source = Path(original_config_entries[0]['source'])
    original_channelmap = Path(channelmap_source)
    if not original_channelmap.is_absolute():
        original_channelmap = config_source.parent / original_channelmap
    mapping = manifest.get('snapshotPaths', {})
    matches = [value for key, value in mapping.items() if os.path.normcase(os.path.abspath(key)) == os.path.normcase(os.path.abspath(original_channelmap))]
    if len(matches) != 1:
        raise ValueError('channelmap has no unique approved snapshot mapping')
    channelmap = snapshot(matches[0])
    program_root = secure_path(ROOT / address.get('immutableProgramSourceRoot', address['programSourceRoot']), run)
    if not channelmap.is_relative_to(program_root):
        raise ValueError('channelmap must belong to the frozen program source tree')
    return {'channelmap': channelmap, 'channelmapSha256': sha256_plaintext(channelmap),
            'originalProjectConfig': config_file, 'pipelineCacheKey': manifest.get('pipelineCacheKey')}


def prepare_runtime(run, channelmap):
    """Use trusted code and a minimal, fully run-owned parser address book.

    sch_parse reads NETLIST, adjacent sch_confirmed.json and inputs.channelmap;
    proj_config additionally hashes every configured input/derived value. Thus
    copying the production config unchanged would read production VS files.
    Keep only the actual semantic dependency and the original output mappings.
    """
    runtime = secure_path(run / f'schematic-runtime-{secrets.token_hex(8)}', run)
    runtime.mkdir()
    scripts = secure_path(ROOT / 'scripts', ROOT)
    for directory, dirs, files in os.walk(scripts, followlinks=False):
        for name in dirs + files:
            secure_path(Path(directory) / name, scripts)
    shutil.copytree(scripts, runtime / 'scripts', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    config = {'project': 'DALI', 'project_dir': 'project/DALI',
              'inputs': {'channelmap': str(channelmap)},
              'intermediates': {
                  'component_statistic': 'project/DALI/Output_Global_Material/schematic/Component-Statistic.txt',
                  'component_statistic_text': 'project/DALI/Output_Global_Material/schematic/Component-Statistic.txt',
                  'sch_connect_map': 'project/DALI/Output_Global_Material/schematic/SCH-Connect-Map.txt',
                  'sch_connect_map_text': 'project/DALI/Output_Global_Material/schematic/SCH-Connect-Map.txt'}}
    (runtime / 'project_config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return runtime


@contextlib.contextmanager
def engine_context(inputs, out, runtime=None):
    import generate_schematic_txt as generator
    import validate_schematic_outputs as validator
    saved = (generator.ROOT, generator.INPUT_ROOT, generator.relative,
             validator.ROOT, validator.INPUT, validator.OUT, dft_source.schematic_output_dir)
    stage_env = os.environ.get('PTC_SCHEMATIC_STAGE_DIR')
    try:
        generator.INPUT_ROOT = inputs
        generator.ROOT = runtime or ROOT
        generator.relative = lambda value: Path(value).resolve().relative_to(ROOT.resolve()).as_posix()
        validator.ROOT = ROOT
        validator.INPUT = inputs
        validator.OUT = out
        dft_source.schematic_output_dir = lambda: out
        # The original generator's stage override cannot redirect training writes.
        os.environ['PTC_SCHEMATIC_STAGE_DIR'] = str(out)
        yield generator, validator
    finally:
        (generator.ROOT, generator.INPUT_ROOT, generator.relative,
         validator.ROOT, validator.INPUT, validator.OUT, dft_source.schematic_output_dir) = saved
        if stage_env is None:
            os.environ.pop('PTC_SCHEMATIC_STAGE_DIR', None)
        else:
            os.environ['PTC_SCHEMATIC_STAGE_DIR'] = stage_env


def execute(action, *, run_root, input_root, out_dir, source, confirmed, cbit):
    run, inputs, out, source, confirmed, cbit = training_layout(input_root, out_dir, run_root, source, confirmed, cbit)
    dependencies = load_dependencies(run, source, confirmed, cbit)
    if action == 'statistic':
        output = secure_path(out / 'Component-Statistic.txt', out)
        if any((out / name).exists() for name in NAMES if name != output.name):
            raise ValueError('statistic-only training cannot adopt full schematic products')
        command = [sys.executable, '-X', 'utf8', str(ROOT / 'scripts/generate_component_statistic_only.py'),
                   '--source', str(source), '--confirmed', str(confirmed),
                   '--channelmap', str(dependencies['channelmap']), '--out', str(output)]
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                   encoding='utf-8', timeout=25, check=False)
        if completed.returncode != 0:
            raise RuntimeError(f'statistic-only producer failed: {completed.stderr[:500]}')
        produced = json.loads(completed.stdout)
        if (produced.get('status') != 'STATISTIC_ONLY' or produced.get('outputPath') != str(output)
                or produced.get('sourceSha256') != sha256_plaintext(source)
                or produced.get('confirmedSha256') != sha256_plaintext(confirmed)
                or produced.get('channelmapSha256') != dependencies['channelmapSha256']
                or produced.get('outputSha256') != hashlib.sha256(output.read_bytes()).hexdigest()):
            raise ValueError('statistic-only producer evidence differs from frozen inputs or output')
        load_dependencies(run, source, confirmed, cbit)
        return {'role': 'schematic-expert', 'mode': 'STATISTIC_ONLY', 'status': 'generated',
                'gate': None, 'canonicalInput': {'path': str(source), 'sha256': produced['sourceSha256']},
                'requiredOutputs': [str(output)], 'outputSha256': produced['outputSha256'],
                'trainingContext': {'runId': run.name, 'pipelineCacheKey': dependencies['pipelineCacheKey']}}
    runtime = None
    if action == 'generate':
        if 'SCH' not in source.name.upper() or source.suffix.lower() != '.csv':
            raise ValueError('original parser requires a unique SCH-named CSV snapshot')
        runtime = prepare_runtime(run, dependencies['channelmap'])
    elif action != 'validate':
        raise ValueError('unsupported training schematic action')
    with engine_context(inputs, out, runtime) as (generator, validator):
        if action == 'generate':
            argv = sys.argv
            try:
                sys.argv = ['generate_schematic_txt.py', '--source', str(source), '--confirmed', str(confirmed),
                            '--cbit', str(cbit), '--out-dir', str(out),
                            '--expected-source-sha', sha256_plaintext(source),
                            '--expected-confirmed-sha', sha256_plaintext(confirmed),
                            '--expected-cbit-sha', sha256_plaintext(cbit)]
                with contextlib.redirect_stdout(io.StringIO()):
                    if generator.main() != 0:
                        raise RuntimeError('original schematic generator did not pass')
            finally:
                sys.argv = argv
        # Recheck snapshots after generation before certifying a result.
        load_dependencies(run, source, confirmed, cbit)
        report = validator.validate(source, confirmed)
    report['trainingContext'] = {'runId': run.name, 'validator': 'scripts/validate_schematic_outputs.py',
                                 'channelmap': str(dependencies['channelmap']),
                                 'channelmapSha256': dependencies['channelmapSha256'],
                                 'pipelineCacheKey': dependencies['pipelineCacheKey']}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--action', choices=['generate', 'validate', 'statistic'], required=True)
    for name in ['run-root', 'input-root', 'out-dir', 'source', 'confirmed', 'cbit']:
        parser.add_argument(f'--{name}', type=Path, required=True)
    args = vars(parser.parse_args())
    try:
        report = execute(**args)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        print(json.dumps({'role': 'schematic-expert', 'gate': 'SCHEMATIC_OUTPUT', 'status': 'blocked',
                          'missingOrStaleOutputs': [str(error)]}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] in ('ready', 'generated') else 2


if __name__ == '__main__':
    raise SystemExit(main())
