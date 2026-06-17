---
name: cocos-vertical-ui-layout
description: Build or refactor vertical Cocos Creator UI with constraint-style layout, safe text bounds, modal layering, and multi-resolution resilience. Use when creating or adjusting portrait mobile game screens, popups, HUDs, inventory grids, equipment slots, or fixing overlap/clipping in Cocos UI.
---

# Cocos Vertical UI Layout

Use this personal skill for portrait mobile UI in Cocos Creator. Be strict about layout hygiene: the goal is not just to make one screenshot look correct; the layout must survive text changes, asset swaps, and common phone aspect ratios. Keep guidance portable across projects; inspect local conventions first, then apply these constraints.

## Start By Reading The Local Patterns

Before editing, inspect the project for existing:

- Design resolution and fit policy.
- Canvas, Widget, Layout, SafeArea, or custom layout constants.
- UI factory/helper modules.
- Existing modal, panel, button, label, bar, and slot creation patterns.
- Current art resource loading and fallback behavior.

Follow existing project conventions unless they are the source of the bug.

## Layout Rules

Use constraint-style thinking even when writing manual coordinates:

- Define panel `width`, `height`, `padding`, and safe bounds first.
- Derive child positions from panel edges and padding.
- Do not treat a label's center point as its left boundary.
- Do not scatter magic coordinates through the code; group layout constants near the top of the module or in a layout config.
- If a parent panel moves or resizes, children should need little or no manual adjustment.
- Prefer semantic groups: top HUD, main visual, left rail, inventory grid, resource strip, story panel, modal layer.
- Fixed-format elements such as slots, buttons, bars, and grids must have stable sizes so hover/selection/text changes cannot shift layout.
- Put coordinates and sizes for major panels in named constants with comments that explain what to tune.
- Align groups by shared edges or centers. When a user says two groups should line up, expose the controlling constants rather than burying the relation in one-off numbers.
- Prefer distributing repeated slots by left edge, right edge, count, and gap calculation instead of hand-entering every x position.

When available, use Cocos `Widget` and `Layout` for simple anchored UI. Use manual coordinates only when the game needs a carefully art-directed composition.

## Tuning Constant Pattern

For art-directed screens, add a compact layout block near the UI module:

```ts
const HUD_LAYOUT = {
  // Main design resolution: adjust this group to move the whole screen section.
  mainVisual: { x: 0, y: 120, width: 560, height: 340 },
  leftRail: { centerX: -285, topY: 120, slot: 64, gap: 8 },
  inventory: { leftX: -260, rightX: 260, y: -210, columns: 7, slot: 62 },
  story: { x: 0, y: -360, width: 590, height: 190 },
};
```

The exact names can follow the project, but the intent should be obvious. If a panel has children, compute child positions from the parent dimensions and padding.

## Text Rules

Every label needs a bounded rectangle:

- Set width and height intentionally.
- Set `lineHeight` for multiline text.
- Use shrink/ellipsis/wrap behavior appropriate to the label.
- Long localized text must not overlap adjacent controls.
- Buttons should have enough internal padding for the longest expected label.
- Story/dialog text needs the cleanest background and largest safety area.

After changing text layout, check:

- Title inside bounds.
- Section headers inside bounds.
- Body text not under buttons.
- Empty-state text not covered by headers or attribute grids.
- Numbers and labels separated enough to scan.

## Modal And Layering Rules

For popups:

- Add a full-screen semi-transparent mask below the popup.
- Pause or block gameplay input if the popup is modal.
- Put equipment details, shops, choices, notices, and logs on predictable layers.
- New popup types must not appear behind existing choice/shop/detail panels.
- Buttons remain inside the popup padding and away from body text.
- Closing/confirming must restore game state and input correctly.

Use a shared notice/toast/modal pattern for important feedback such as full inventory, insufficient currency, locked slots, or ad reward results.

## Asset Replacement Rules

When swapping placeholder art for final UI assets:

- Keep the logical layout dimensions stable first; tune art borders after.
- Nine-slice panels should not depend on a specific screenshot crop.
- Do not let decorative corners or glow change hit boxes unless the user explicitly wants that.
- If an imported image looks stretched, determine whether the problem is the source art, the nine-slice border, or the runtime node size before changing layout.
- Remove temporary solid-color backgrounds and debug outlines once the art asset is reliable.

## Portrait Screen Checklist

Before calling a layout done, verify these on the design resolution and at least one browser/device preview:

- Top HUD does not collide with status/browser chrome.
- Main visual is not squeezed by decorative panels.
- Left/right rails keep equal or intentional margins.
- Inventory grids align to fixed left/right anchors and distribute evenly.
- Story/dialog panel is readable and not too low or clipped.
- Bottom buttons are visible and tappable.
- Modal mask covers the whole game.
- No label, button, slot, or panel overlaps incoherently.
- Popup contents remain inside the panel at 75%, 100%, and any project-specific modal scale.
- Equipment or inventory detail views do not place section titles outside the panel.

For Cocos Creator projects, respect the configured design resolution and fit-width/fit-height settings. Do not compensate for preview scaling by hardcoding browser-specific offsets.

## Implementation Pattern

When writing code:

1. Add or update named layout constants.
2. Build parent groups first.
3. Compute child positions from parent dimensions.
4. Create labels with fixed bounds.
5. Apply art skins without changing layout dimensions.
6. Keep graphics fallback if runtime assets may be missing.
7. Add comments only to explain layout intent and manual tuning knobs.

Prefer extracting large UI sections into modules or builders when a single controller becomes hard to reason about.

## Verification

Run the project's normal type/build checks when available, for example:

- `tsc --noEmit`
- Cocos preview/build command if the project has one.
- Any local UI screenshot or browser preview workflow.

If automated visual checks are unavailable, manually inspect the highest-risk screens: main HUD, equipment detail, shop, choice modal, log/archive, notice popup, and settlement.

## Report Back

Summarize:

- Which layout groups changed.
- Which constants control future tuning.
- Which screens were checked.
- Any remaining risk, especially text overflow, asset border tuning, or device adaptation.
