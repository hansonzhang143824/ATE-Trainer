const RUN_ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const RESERVED = /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i;

export function trainingAddressBook(runId) {
  if (typeof runId !== 'string' || !RUN_ID.test(runId) || /[. ]$/.test(runId) || RESERVED.test(runId)) {
    throw new Error('invalid training run id');
  }
  const runRoot = `Training_Materials/runs/${runId}`;
  const inputRoot = `${runRoot}/input`;
  const profileRoot = `${runRoot}/profile`;
  return Object.freeze({
    runRoot, inputRoot, workbook: `${inputRoot}/Dali_testmode.xlsx`,
    sourceView: `${inputRoot}/dft-source-view.json`,
    special: `${inputRoot}/DALI-special-information.json`, rules: `${inputRoot}/DFT解析规则.txt`,
    dftRoot: `${runRoot}/input-sync/dft`, verificationRoot: `${runRoot}/verification`,
    profileRoot, instructions: `${profileRoot}/instructions.md`,
  });
}

export function trainingDftCommands(address, tm, sourceSha) {
  if (!/^TM[0-9]+$/.test(tm)) throw new Error('invalid training test item');
  if (sourceSha !== '<SOURCE_SHA>' && !/^[a-f0-9]{64}$/.test(sourceSha)) throw new Error('invalid source digest');
  const output = `${address.dftRoot}/${tm}`;
  return {
    hash: `python scripts/hash_ate_plaintext.py ${address.workbook}`,
    refresh: `python scripts/refresh_dft_meta_from_source.py --source ${address.workbook} --tm ${tm} --meta ${output}/dft-meta.json --expected-sha ${sourceSha} --input-root ${address.runRoot}`,
    render: `python scripts/render_dft_conditions_yaml.py --tm ${tm} --out ${output}/dft-conditions.yaml --expected-sha ${sourceSha} --workbook ${address.workbook}`,
    validate: `python scripts/validate_dft_outputs.py --tm ${tm} --workbook ${address.workbook} --output-dir ${output}`,
  };
}
