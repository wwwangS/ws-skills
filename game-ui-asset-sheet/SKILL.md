---
name: game-ui-asset-sheet
description: Generate, evaluate, and prepare sliceable 2D game UI asset sheets from a confirmed reference design. Use when creating production UI art assets with image generation, converting a UI concept into reusable panels/buttons/slots, or checking that generated UI assets are sliceable, text-free, and nine-slice friendly.
---

# Game UI Asset Sheet

Use this personal skill when the task is to make **usable UI art assets**, not another mockup. Be strict: the main failure mode is generating a beautiful full-screen design that cannot be sliced or reused. Keep the workflow portable across projects; local project scripts are preferred when they exist, but do not bake one project's paths or naming into the skill.

## First, Classify The Output

Before generating anything, state which one is needed:

- **Reference screen**: a full UI mockup used to choose style and layout.
- **Asset sheet**: separated components arranged on a neutral background for slicing.
- **Runtime slices**: individual transparent PNG/SpriteFrame assets used by the game.

Do not mix these. If the user asks for assets, do not produce a full screen layout unless they explicitly ask for a reference screen first.

## Required Inputs

Identify or ask for:

- The **current approved reference design**. Do not infer style from memory when a reference image exists.
- Target engine and constraints: Cocos, Unity, Godot, web canvas, etc.
- Target resolution or design aspect ratio.
- Asset list: panels, buttons, slots, modals, bars, icons, ornaments.
- Whether assets must support nine-slice scaling.
- Whether the user wants you to generate new art, slice existing art, or only review an asset sheet.

If the approved reference design is ambiguous or there are multiple competing designs, ask the user to pick one. Generating from the wrong design wastes the entire pass.

## Confirmation Before Image Generation

Before calling image2/imagegen or any image generation tool, confirm these three things with the user:

- **Reference**: which image/design is the current approved source.
- **Output type**: reference screen, asset sheet, or runtime slices.
- **Prompt summary**: the short version of what will be generated and the key constraints.

Do not call image generation until the user confirms, unless the user explicitly says to generate directly or gives an equivalent instruction such as "不用问，直接出图".

## Generation Rules

For asset sheets:

- Use the approved reference design's visual language; do not redesign from a loosely related style.
- Arrange components as separate isolated pieces with generous spacing.
- No full-screen UI layout unless the requested output is a reference screen.
- No readable text, numbers, labels, fake Chinese, fake English, logos, or watermarks.
- No gameplay content unless requested: avoid ships, characters, enemies, item art, and backgrounds inside reusable UI frames.
- Keep stretchable centers clean: low contrast, no symbols, no faces, no strong texture, no focal ornaments.
- Put detail on protected borders, corners, caps, and separate ornaments.
- Avoid excessive protrusions around common buttons and small plaques; large decorative wings/spikes reduce usable layout space.
- Generate assets larger than runtime size when possible; downscaling is safer than upscaling.

For nine-slice assets:

- Corners and caps can be ornate.
- Center and edge stretch zones must be visually simple.
- Repeating or directional texture in the stretch zone is a bug.
- If a badge, crest, skull, gem, seal, or character is needed, make it a separate overlay asset, not part of the scalable base.

For slots:

- Keep one geometry across rarity states.
- Rarity should primarily change border color/glow, not shape or center art.
- Empty, locked, selected, and filled states should be separate or clearly layerable.
- Do not bake item icons into generic slot frames.

## Prompt Template

Use and adapt this structure:

```text
Use case: production UI asset sheet
Asset type: production-ready 2D game UI asset sheet for slicing into <engine> UI resources.
Reference image: Use the attached/approved reference design as the exact style and component reference. Ignore all text, numbers, labels, and gameplay content. Do not redesign from another style.

Primary request: Create a complete usable UI asset sheet, not a full game screen mockup.
Canvas/composition: <size> dark neutral background. Arrange every UI component as separate isolated pieces with generous spacing. No overlapping. No full-screen layout. Every component must be complete and easy to crop.

Style to preserve: <short style tokens from approved reference>.

Required separate assets:
1. <asset>
2. <asset>
...

Critical constraints: No readable text, no numbers, no letters, no watermark, no logo. No full-screen layout. Keep centers clean for nine-slice scaling; decoration stays on borders/corners. No unnecessary extra ornaments beyond the reference.
```

## Evaluate Before Slicing

Reject and regenerate if any of these are true:

- It became a full-screen UI instead of an asset sheet.
- It includes readable text, numbers, fake glyphs, or labels.
- It follows the wrong reference design.
- Common buttons or plaques have large decorative protrusions that consume layout space.
- Stretchable centers contain important art, high contrast texture, or symbols.
- Components overlap or are cropped.
- It bakes gameplay content into generic reusable UI assets.
- The story/dialog paper is too busy for reading.

If only minor issues exist, list them before slicing and ask whether to proceed or regenerate.

For a stricter pass/fail review of an image-generated asset sheet, read `references/asset-sheet-review.md`.

## Slicing Strategy

Choose the least surprising tool for the project:

1. If the project already has a working asset slicing pipeline, inspect and reuse it.
2. If the existing pipeline is duplicated or brittle, improve it by extracting shared helpers before replacing it.
3. If no project pipeline exists, use the bundled manifest-driven Pillow script at `scripts/slice_ui_asset_sheet.py`.
4. Use TexturePacker or engine atlas tools for packing many separate PNGs into atlases, not as the primary way to cut an image-generation asset sheet into reusable components.
5. Use manual editor slicing only for one-off assets or when the user wants direct visual control.

For Cocos projects, prefer generating `.meta` files only when the project expects checked-in meta files. Dynamic metadata must use the real output image width and height; never hardcode 128x128 sprite data for arbitrary assets.

## Manifest Pattern

When slicing assets with the bundled script, create a JSON manifest next to the source sheet. Keep paths relative to the manifest file unless absolute paths are necessary.

```json
{
  "source": "asset_sheet.png",
  "outputDir": "runtime_slices",
  "contactSheet": "runtime_slices_contact.png",
  "defaults": {
    "trim": false,
    "padding": 0,
    "cocosMeta": true,
    "pixelsToUnit": 100
  },
  "backgroundRemoval": {
    "mode": "none"
  },
  "assets": [
    {
      "name": "story_panel",
      "rect": [32, 48, 420, 180],
      "out": "story_panel.png",
      "nineSlice": { "left": 32, "right": 32, "top": 32, "bottom": 32 }
    },
    {
      "namePrefix": "item_",
      "grid": { "rect": [0, 0, 1024, 1024], "cols": 5, "rows": 5, "count": 25 },
      "names": ["item_a", "item_b"],
      "trim": true,
      "fit": { "width": 128, "height": 128, "max": 108 }
    }
  ]
}
```

Run:

```bash
python scripts/slice_ui_asset_sheet.py path/to/slice_manifest.json
```

Use project-local dependencies if present. Install Pillow only when needed.

### Transform vs. nine-slice (hard rule)

`trim` / `fit` and `nineSlice` are mutually exclusive. Trimming crops to the
alpha bounding box, and fitting rescales the art without recalculating the
declared border rectangle. Either one can silently break stretch zones. The
bundled script refuses these combinations.

- Icons / item art: `trim: true`, no `nineSlice` — crop tight and center.
- Panels / buttons / bars / slot frames: `nineSlice` set, `trim: false`, no
  `fit` — keep the full rect so borders stay aligned.
- If a nine-slice asset needs a different size, resize the source art upstream
  or add a non-sliced variant; do not use the slicer's `fit` option.


## Persist Project Assets

When assets are meant for a project:

- Save the source sheet into the project's design/generated area or equivalent.
- Create a contact sheet or preview of final slices.
- Save runtime slices into the engine resource directory.
- Preserve the original generated file unless the user explicitly asks to delete it.
- Document the source image, crop assumptions, and intended nine-slice border values.
- Keep the slicing manifest with the source sheet so the output can be regenerated.
- Record any manual Cocos nine-slice border values that still need engine-side tuning.

## Handoff Notes

At the end, report:

- Source sheet path.
- Runtime slice directory.
- Contact sheet path.
- Assets generated.
- Slicing manifest path, if used.
- Known issues that need manual art or engine-side border tuning.
