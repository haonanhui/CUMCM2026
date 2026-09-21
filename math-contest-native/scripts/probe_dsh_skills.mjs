// Exercise the installed DSH filesystem provider, without booting a model session.
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
const entry = process.argv[2];
if (!entry) throw new Error('Pass the installed dsh-skill-filesystem/lib/index.js path');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { FileSystemSkillProvider } = await import(pathToFileURL(path.resolve(entry)).href);
const warnings = [];
const abort = new AbortController();
const provider = new FileSystemSkillProvider(
  { get: () => undefined, logger: { warn: (value) => warnings.push(String(value)) } },
  { signal: abort.signal, invalidate: () => {} },
  { includeDefaultRoots: false, customSkillDirs: [path.join(root, '.agents/skills')], watch: false }
);
try {
  const listed = await provider.list({ cwd: root, signal: abort.signal });
  const candidates = Array.isArray(listed) ? listed : listed.candidates;
  const loaded = [];
  for (const candidate of candidates) {
    const body = await provider.get(candidate, { cwd: root, signal: abort.signal });
    if (!body?.content?.length) throw new Error('Body load failed');
    loaded.push({ name: body.name, path: body.path, bodyCharacters: body.content.length });
  }
  console.log(JSON.stringify({ providerListedAndRead: loaded, warnings, modelTurns: 0 }, null, 2));
  const expected = fs.readdirSync(path.join(root, '.agents/skills'), { withFileTypes: true })
    .filter(item => item.isDirectory() && !item.name.startsWith('_') &&
      fs.existsSync(path.join(root, '.agents/skills', item.name, 'SKILL.md')))
    .map(item => item.name).sort();
  if (JSON.stringify(loaded.map(item => item.name).sort()) !== JSON.stringify(expected) || warnings.length) process.exitCode = 1;
} finally {
  await provider.dispose();
}
