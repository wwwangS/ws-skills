# Asset Sheet Review

Use this reference when judging whether a generated UI asset sheet should be sliced.

## Pass Conditions

- The sheet contains isolated reusable components, not a full game screen.
- Components are complete, uncropped, and separated by enough empty space to crop safely.
- Generic components contain no readable text, numbers, fake glyphs, logos, or watermarks.
- Scalable panels have clean centers and stable edges.
- Ornament density matches the approved reference without adding new dominant motifs.
- Small buttons and stat plaques do not have wide protruding wings that steal layout space.
- Story or dialog backgrounds preserve high text contrast.
- Slot frames have consistent geometry across rarity or state variants.

## Regenerate Conditions

- Wrong style reference.
- Full mockup instead of asset sheet.
- Text is baked into reusable art.
- Stretch zones contain skulls, crests, faces, strong texture, or directional patterns.
- Components overlap, touch, or are cut off.
- A generic frame includes gameplay art such as a ship, character, enemy, or item icon.

## Proceed With Warning

Minor defects may be acceptable if the user prefers speed:

- Slight color mismatch that can be tinted in engine.
- Extra corner decoration that will be cropped out.
- One component is unusable but the rest of the sheet is strong.
- Nine-slice borders may need manual tuning in the engine.
