import { execFile as execFileCallback } from 'node:child_process';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);

/** The existing gate hashes canonical plaintext and verifies both review bindings. */
export async function checkDftReuse(workspaceRoot, targetTms, run = execFile) {
  const reports = [];
  for (const tm of targetTms) {
    if (!/^TM\d+$/.test(tm)) throw new Error('Invalid DFT test item');
    let stdout;
    let exitCode = 0;
    try {
      ({ stdout } = await run('python', ['scripts/validate_dft_outputs.py', '--tm', tm], {
        cwd: workspaceRoot, windowsHide: true, encoding: 'utf8',
        timeout: 30_000, maxBuffer: 1024 * 1024,
      }));
    } catch (error) {
      if (error.code !== 2 || error.killed) throw error;
      stdout = error.stdout;
      exitCode = 2;
    }
    const report = JSON.parse(stdout);
    if (report.gate !== 'DFT_OUTPUT' || !['ready', 'stale'].includes(report.status)
        || !/^[a-f0-9]{64}$/.test(report.canonicalInput?.sha256)
        || !Array.isArray(report.requiredOutputs) || report.requiredOutputs.length !== 3
        || !Array.isArray(report.missingOrStaleOutputs)
        || (report.status === 'ready' ? exitCode !== 0 || report.missingOrStaleOutputs.length !== 0
          : exitCode !== 2 || report.missingOrStaleOutputs.length === 0)) {
      throw new Error(`Invalid DFT_OUTPUT preflight for ${tm}`);
    }
    reports.push({ tm, exitCode, ...report });
  }
  return { unchanged: reports.length > 0 && reports.every((r) => r.status === 'ready'), reports };
}
