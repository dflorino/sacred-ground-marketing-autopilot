#!/usr/bin/env node
/**
 * Validates required transparent layers exist before Remotion render.
 * Run: npm run validate:layers -- --slug living-crystal-morning-machine
 */
import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.join(__dirname, '..', '..');
const publicDir = path.join(__dirname, '..', 'public', 'layers');

const slugArg = process.argv.find((a, i) => process.argv[i - 1] === '--slug');
const slug = slugArg || 'living-crystal-morning-machine';

// Map slug → style_id for manifest lookup
const styleId = slug.replace(/^living-/, 'living_').replace(/-/g, '_');
const manifestPath = path.join(
  repoRoot,
  'data',
  'living_worlds',
  'layers',
  styleId,
  'manifest.json',
);

let required = [];
let optional = [];

if (fs.existsSync(manifestPath)) {
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  required = manifest.required_layers || [];
  optional = manifest.optional_layers || [];
} else {
  console.warn('No manifest at', manifestPath, '— using crystal machine defaults');
  required = [
    'background-plate.png',
    'coffee-cup.png',
    'candle-body.png',
    'candle-flame.png',
    'candle-glow.png',
    'incense-holder.png',
    'hero-crystal.png',
    'pendant.png',
    'card-front.png',
    'card-back.png',
    'open-sign.png',
    'lever.png',
    'kettle.png',
    'gear.png',
  ];
  optional = [
    'foreground-frame.png',
    'coffee-steam-1.png',
    'coffee-steam-2.png',
    'coffee-steam-3.png',
    'incense-smoke-1.png',
    'incense-smoke-2.png',
    'incense-smoke-3.png',
    'crystal-highlight.png',
    'reader.png',
    'reader-hand.png',
  ];
}

const layerDir = path.join(publicDir, slug);

let ok = true;
const missing = [];

for (const file of required) {
  const p = path.join(layerDir, file);
  if (!fs.existsSync(p)) {
    missing.push(file);
    ok = false;
  }
}

if (ok) {
  console.log('✓ All', required.length, 'required layers present in', layerDir);
} else {
  console.error('✗ Missing required layers for', slug, ':');
  missing.forEach((f) => console.error('  -', f));
  console.error('\nSee docs/LIVING-WORLDS-LAYERS-REPO.md — decompose scene before render.');
  process.exit(1);
}

const presentOptional = optional.filter((f) => fs.existsSync(path.join(layerDir, f)));
if (presentOptional.length) {
  console.log('Optional layers found:', presentOptional.join(', '));
}
