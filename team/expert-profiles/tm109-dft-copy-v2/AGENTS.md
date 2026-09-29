# PTC DFT Expert training conversation

This directory is the editable DFT expert profile for a DSH-native training
session. It is not a project-delivery run. Do not start the DFT business flow,
read TM109 source materials, run a business gate, dispatch another expert, or
advance a batch merely because this conversation was opened.

For the current `SMOKE_ONLY` check, when asked `1+2等于几，把答案写在JSON里`, reply
with JSON containing a numeric answer: `{"answer":3}`. The chat response is
conversation evidence only; the control-plane smoke run independently launches
a fresh child and verifies its own receipt.

When the user explicitly asks to improve this expert, work only on the editable
profile files in this directory (`instructions.md`, `profile.yaml`, and
`output-contract.schema.json`). Do not edit published `versions/` in place.
The workbench's Save and Freeze actions determine which candidate is retained
and which immutable snapshot is used for the arithmetic training run.
