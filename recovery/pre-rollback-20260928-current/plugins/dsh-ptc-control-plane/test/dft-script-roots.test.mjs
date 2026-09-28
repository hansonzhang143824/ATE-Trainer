import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../../..');

function source(name) {
  return fs.readFileSync(path.join(ROOT, 'scripts', name), 'utf8');
}

test('DFT scripts expose optional training-root flags and retain legacy arguments', () => {
  const validate = source('validate_dft_outputs.py');
  const refresh = source('refresh_dft_meta_from_source.py');
  const render = source('render_dft_conditions_yaml.py');
  assert.match(validate, /add_argument\("--tm", required=True\)/);
  assert.match(validate, /add_argument\("--workbook", type=Path\)/);
  assert.match(validate, /add_argument\("--output-dir", type=Path\)/);
  assert.match(refresh, /add_argument\('--source',type=Path,required=True\)/);
  assert.match(refresh, /add_argument\('--input-root',type=Path\)/);
  assert.match(render, /add_argument\('--out', required=True\)/);
  assert.match(render, /add_argument\('--workbook', type=Path\)/);
});

test('validate reads only the three fixed artifacts under an explicit output directory', () => {
  const validate = source('validate_dft_outputs.py');
  assert.match(validate, /folder = dft_source\.ensure_within\(output_dir, workbook\.parent\.parent\)/);
  assert.match(validate, /else:\n\s+folder = dft_source\.dft_output_dir\(tm\)/);
  assert.match(validate, /folder \/ "dft-meta\.json", folder \/ "dft-conditions\.yaml", folder \/ "dft-semantic-review\.json"/);
  assert.match(validate, /validate\(args\.tm, args\.workbook, args\.output_dir\)/);
});

test('refresh preserves the production default and binds explicit input roots to one canonical workbook', () => {
  const refresh = source('refresh_dft_meta_from_source.py');
  assert.match(refresh, /if args\.input_root is not None:/);
  assert.match(refresh, /dft_source\.ensure_within\(source,input_root\)/);
  assert.match(refresh, /source!=dft_source\.discover_workbook\(input_root\)\.resolve\(\)/);
  assert.match(refresh, /dft_source\.ensure_within\(args\.meta,material_root\)/);
  assert.match(refresh, /dft_source\.ensure_within\(source,dft_source\.INPUT_ROOT\)/);
  assert.match(refresh, /source!=dft_source\.discover_workbook\(\)\.resolve\(\)/);
});

test('render preserves discovery by default and bounds explicit workbook output', () => {
  const render = source('render_dft_conditions_yaml.py');
  assert.match(render, /if args\.workbook is not None:/);
  assert.match(render, /workbook = args\.workbook\.resolve\(\)/);
  assert.match(render, /dft_source\.ensure_within\(args\.out, workbook\.parent\.parent\)/);
  assert.match(render, /else:\n\s+workbook = dft_source\.discover_workbook\(\)/);
});
