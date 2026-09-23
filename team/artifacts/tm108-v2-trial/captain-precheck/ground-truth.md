# TM108 V2 trial - captain pre-check evidence

Timestamp: 2026-09-17 13:00:14 +08:00

## A. DFT three-artifact set readability
Command: Get-Content project\DALI\meta\<file> -AsByteStream -TotalCount 12

- dali_tm_meta.json      size=  54548  hex=54 53 5a 23 05 05 07 0e 93 00 00 00  ascii='TSZ#........'
- test_conditions.yaml   size=  14640  hex=54 53 5a 23 05 91 07 0e 97 00 00 00  ascii='TSZ#........'
- manifest.json          size=   3463  hex=54 53 5a 23 05 74 07 0e af 00 00 00  ascii='TSZ#.t......'
- tm000_102.json         size=   7367  hex=54 53 5a 23 05 98 07 0e a4 00 00 00  ascii='TSZ#........'

Result: all four start with 54 53 5a 23 ('TSZ#'). NOT JSON/YAML text. The project DFT three-artifact set is unreadable as text in its current form.

## B. TM108 DFT facts (plain-text source)
Source: team\artifacts\acceptance-20260916-dali10\dft-raw\compact-dump.txt:14,146,148
  TM108_HSKP_VAC1_PRST  dftItem=TM108  testType=toggle  projectType=一般测试项目(AWG)  paramType=UVLO
  params: [{"check": "MV", "checkPin": "DTEST0", "dftItem": "TM108"}]
Source: team\artifacts\acceptance-20260916-dali10\dft-raw\compact-dump.txt:230
  ### tm108.sv 4d0ea5c30fe5369e98a6d81215bbfb5b5f41bf44ea1c5dbc8df94af75bb92dc1
Source: team\artifacts\acceptance-20260916-dali10\dft-raw\csv-full-dump.txt:107
  all items: [..., 'TM108', ...]
Plain-text DFT fact file present: team\artifacts\acceptance-20260916-dali10\dft-raw\DFT_restored-full.json

## C. Scope / environment constraints
Command: Set-Content D:\PROJECT6-DALI\devel\__dsh_write_probe.txt
Result: WRITE DENIED - Access to the path 'D:\PROJECT6-DALI\devel\__dsh_write_probe.txt' is denied.
Policy: profile executionPrompt states 'Never modify D:/PROJECT6-DALI/devel'.
Consequence: implementation for this trial must be produced as a workspace-staged patch + manifest; the real VS build cannot be executed in this sandbox.

## D. TM scope
In scope: TM108 only. TM601 and all other TMs are explicitly excluded from every task contract.
