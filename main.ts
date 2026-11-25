// Copies the rendered poster (entry.png) into the directory named by
// MAKEFUN_OUTPUT_DIR (default: out/). Standard library only.
import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, "entry.png");
const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "out");

if (!existsSync(source)) {
  console.error(
    `error: ${source} not found. Render it first with: python3 draw25.py entry.png`,
  );
  process.exit(1);
}

try {
  mkdirSync(outDir, { recursive: true });
  const target = join(outDir, "entry.png");
  copyFileSync(source, target);
  console.log(`copied entry.png (${statSync(target).size} bytes) to ${outDir}`);
} catch (err) {
  console.error(`error: could not write to ${outDir}: ${(err as Error).message}`);
  process.exit(1);
}
