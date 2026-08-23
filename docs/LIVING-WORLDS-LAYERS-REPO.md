# Living Worlds layer repository (GitHub)

All 20 Morning Living Worlds concepts share one **layer repo layout** in this project. Founder approves looks here before any calendar assignment or publish.

## Directory layout

```
assets/living_worlds/<slug>/
  scene-raw.png              # Hero plate (no baked schedule text)
  layers/
    background-plate.png     # Scene with moving objects removed
    hero-crystal.png
    pendant.png
    candle-body.png
    candle-flame.png
    …                        # See manifest per concept

data/living_worlds/layers/<style_id>/
  manifest.json              # Required files + approval state
  status.json                # scene / layers / sync flags
  prompts/
    scene-raw.txt              # AI prompt for hero plate
    decompose-brief.md         # Human + agent decomposition guide
    layer-*.txt                # One prompt per required PNG

remotion/public/layers/<slug>/   # Synced copy for `npm run validate:layers`
```

**Slug** = `style_id` with `living_` → `living-` and underscores → hyphens.

## Six anchors (every concept)

Crystal · jewelry · incense · candle · reader · coffee — visible in scene-raw; decomposed into layers for Remotion.

## Text rule

Schedule, reader, date, website, phone → **live React** (`EventPanel` in Remotion). Never bake into PNG layers.

## Commands

```bash
python3 -m marketing living-world-layers init --all
python3 -m marketing living-world-layers status
python3 -m marketing living-world-layers pending-scenes
python3 -m marketing living-world-layers register-scene <style_id> <path/to/scene.png>
python3 -m marketing living-world-layers sync
python3 -m marketing living-world-layers validate
```

## Remotion validation

```bash
cd remotion
npm run validate:layers -- --slug living-crystal-morning-machine
```

## Approval fields (`manifest.json` → `approval`)

| Field | Values |
|-------|--------|
| `scene_raw` | `pending` · `present` · `approved` · `rejected` |
| `layers_complete` | `pending` · `partial` · `complete` |
| `founder_look` | `pending` · `approved` · `rejected` |
| `assigned_date` | `null` or `YYYY-MM-DD` |

Update `founder_look` and `assigned_date` only after Founder says yes and picks a date.

## Do not

- Publish `approved_concept` styles until `status: active` in config + assets complete
- Animate flat scene-raw without layer decomposition
- Reuse image URLs (`image_usage` lifetime block)
- Use generic mystic AI wellness template art

See also: `docs/LIVING-WORLDS-LAYER-PREP.md`, `docs/MORNING-LIVING-WORLDS.md`, `.cursor/rules/living-worlds-layers.mdc`
