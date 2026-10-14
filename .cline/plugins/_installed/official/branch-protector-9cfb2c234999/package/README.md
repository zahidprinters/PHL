# branch-protector

Blocks accidental `git push` commands on protected branches.

## What It Does

Registers a `beforeTool` hook that inspects `run_commands` calls. If the command is `git push` on `main`, `master`, or `release/*`, the hook skips the tool call unless the command includes `--force-allow`.

## Install

```bash
cline plugin install branch-protector
```

For local development from this repository:

```bash
cline plugin install ./plugins/branch-protector --cwd .
```

## Example Usage

After installation, use Cline normally:

```text
Commit this change and push the feature branch.
```

If Cline attempts a protected-branch `git push`, `branch-protector` blocks the command before it runs unless the command explicitly includes `--force-allow`.

## Requirements

- A git workspace.
- No API keys or external services.

## Security Notes

This is a guardrail, not a replacement for protected branches in your git host. It only applies to shell commands executed through Cline tools.
