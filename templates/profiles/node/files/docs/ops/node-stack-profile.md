# Node Stack Profile

This repo opted into the `node` repo-contract-kit profile.

The profile adds local Node.js hygiene guidance for agents and maintainers. It
does not install packages, create `node_modules`, generate lockfiles, scaffold a
framework, or assume npm, pnpm, Yarn, or Bun.

## What To Inspect First

- `package.json`
- committed lockfiles: `package-lock.json`, `npm-shrinkwrap.json`,
  `pnpm-lock.yaml`, `yarn.lock`, `bun.lock`, or `bun.lockb`
- config files such as `tsconfig.json`, `eslint.config.*`, `prettier.config.*`,
  framework config, and test config
- existing local docs for build, test, deploy, and release commands

## Agent Rules

- Read `package.json` scripts before running language-specific commands.
- Prefer the package manager indicated by the committed lockfile.
- Do not run dependency installation or lockfile-changing commands unless the
  human explicitly asks for that operation.
- Treat missing scripts as missing evidence, not as permission to invent a
  command.
- Keep repo-contract-kit docs checks separate from application test commands.

## Useful Local Checks

These are hints, not guaranteed commands. Run them only when the matching files
and scripts exist.

```bash
node -e "const p=require('./package.json'); console.log(Object.keys(p.scripts||{}).sort().join('\n'))"
npm test
npm run lint
```

If the repo uses pnpm, Yarn, or Bun, translate only to an equivalent existing
script command and avoid install/update commands unless requested.

## Machine-Readable Hints

The profile also installs:

```text
.agent-workflows/stack-profiles/node.json
```

That file is a local hint document for tools. It is not a package-manager
configuration file and should not be used to infer permission for network or
dependency operations.
