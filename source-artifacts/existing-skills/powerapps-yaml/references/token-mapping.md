# Design tokens → Power Apps values

Power Apps has no Tailwind classes and no CSS variables — every color is an `RGBA(r, g, b, a)` and
every size is a number. This file is how you get from the prototype's tokens to those literals.

## Where the tokens live (read them every run — tokens drift)

Check these in order:
1. **`assets/tailwind-config.js`** — `tailwind.config.theme.extend`: `colors` (hex), `spacing` (px),
   `fontSize` (px). This is usually the single source of truth. Parse the object literal.
2. **`:root { --token: value }`** in a CSS file (`assets/app.css`) — CSS custom properties.
3. **Inline hex / `rgb()`** in the markup when there's no token layer.

A class like `bg-primary` resolves through the config: `primary` → `#3b39c2` → `RGBA(59, 57, 194, 1)`.
Don't hard-code from memory; re-derive from the actual file, because the config gets reconciled and
values change between versions.

## hex → RGBA

`#RRGGBB` → `RGBA(R₁₀, G₁₀, B₁₀, 1)` (each pair from base-16 to base-10). Opacity `1` unless the class
carries an alpha (`/10`, `/50`) → use that fraction as the 4th arg, e.g. `bg-primary-container/10` →
`RGBA(85, 85, 219, 0.1)`.

Examples: `#3b39c2` → `RGBA(59, 57, 194, 1)`; `#ffffff` → `RGBA(255, 255, 255, 1)`;
`#ba1a1a` → `RGBA(186, 26, 26, 1)`; `#fcf8ff` → `RGBA(252, 248, 255, 1)`.

Quick converter:
```bash
python3 -c "h='3b39c2'; print(f'RGBA({int(h[0:2],16)}, {int(h[2:4],16)}, {int(h[4:6],16)}, 1)')"
```

## Layout dimensions: the ~0.8 scale

The prototype is designed at full size; Power Apps targets a large monitor at ~0.8. **Scale layout
dimensions** (widths, heights, sidebar, gaps drawn from spacing tokens) by ≈0.8:

- `spacing.sidebar_width: 260px` → `Width: 208`
- `spacing.container_padding: 32px` → `Padding*: 32` (padding often kept 1:1; scale if cramped)
- `spacing.gutter / stack_lg: 24px` → `LayoutGap: 24`; `stack_md: 16` → `16`; `stack_sm: 8` → `8`

**Text sizes are tuned, not a strict ×0.8** — follow the targets in `yaml-conventions.md` §6
(body 11, section header 12, column header 9, big stat 32, form title 18, floor ≈ 9).

## Ready lookup — current MD3 Tailwind theme

Derived from the project's `assets/tailwind-config.js`. **Verify against the live file each run**; if a
token changed, this table is stale.

### Colors (token → hex → Power Apps)
| Token | Hex | RGBA |
|---|---|---|
| `primary` | `#3b39c2` | `RGBA(59, 57, 194, 1)` |
| `primary-container` | `#5555db` | `RGBA(85, 85, 219, 1)` |
| `primary-fixed` | `#e1dfff` | `RGBA(225, 223, 255, 1)` |
| `primary-fixed-dim` | `#c1c1ff` | `RGBA(193, 193, 255, 1)` |
| `on-primary` | `#ffffff` | `RGBA(255, 255, 255, 1)` |
| `secondary` | `#006879` | `RGBA(0, 104, 121, 1)` |
| `secondary-container` | `#74e3fe` | `RGBA(116, 227, 254, 1)` |
| `tertiary` | `#3c5701` | `RGBA(60, 87, 1, 1)` |
| `tertiary-container` | `#53701c` | `RGBA(83, 112, 28, 1)` |
| `error` | `#ba1a1a` | `RGBA(186, 26, 26, 1)` |
| `error-container` | `#ffdad6` | `RGBA(255, 218, 214, 1)` |
| `on-error-container` | `#93000a` | `RGBA(147, 0, 10, 1)` |
| `background` / `surface` | `#fcf8ff` | `RGBA(252, 248, 255, 1)` |
| `surface-container-lowest` | `#ffffff` | `RGBA(255, 255, 255, 1)` |
| `surface-container-low` | `#f5f2fe` | `RGBA(245, 242, 254, 1)` |
| `surface-container` | `#efecf8` | `RGBA(239, 236, 248, 1)` |
| `surface-container-high` | `#eae6f2` | `RGBA(234, 230, 242, 1)` |
| `surface-container-highest` | `#e4e1ec` | `RGBA(228, 225, 236, 1)` |
| `surface-variant` | `#e4e1ec` | `RGBA(228, 225, 236, 1)` |
| `on-surface` / `on-background` | `#1b1b23` | `RGBA(27, 27, 35, 1)` |
| `on-surface-variant` | `#464554` | `RGBA(70, 69, 84, 1)` |
| `outline` | `#777586` | `RGBA(119, 117, 134, 1)` |
| `outline-variant` | `#c7c4d7` | `RGBA(199, 196, 215, 1)` |

### Status colors (for the badge `Switch()` — see html-to-powerapps §8)
| Token | Hex | RGBA |
|---|---|---|
| `status-pending-bg` | `#aaedff` | `RGBA(170, 237, 255, 1)` |
| `status-pending-text` | `#006879` | `RGBA(0, 104, 121, 1)` |
| `status-completed-bg` | `#ccef8c` | `RGBA(204, 239, 140, 1)` |
| `status-completed-text` | `#3c5701` | `RGBA(60, 87, 1, 1)` |
| `status-rejected-bg` | `#ffdad6` | `RGBA(255, 218, 214, 1)` |
| `status-rejected-text` | `#ba1a1a` | `RGBA(186, 26, 26, 1)` |

### Spacing (token → px → scaled)
| Token | px | Power Apps |
|---|---|---|
| `sidebar_width` | 260 | `208` (×0.8) |
| `container_padding` | 32 | `32` |
| `gutter` / `stack_lg` | 24 | `24` |
| `stack_md` | 16 | `16` |
| `stack_sm` | 8 | `8` |

### Font sizes (token → px → Power Apps `Size`)
Tokens: `display-lg` 32, `headline-md` 24, `title-sm` 18, `body-lg` 16, `body-md` 14, `label-caps` 12.
Map to the tuned targets, not a literal ×0.8: big stat number `Size: 32`, form/page title `Size: 18`,
section header `Size: 12`, body `Size: 11`, caps/column header `Size: 9`. Font family (`Hanken
Grotesk`) has no Power Apps equivalent — use the default (`Font: =Font.'Open Sans'`) or the closest
available; don't invent a font name.

## Border radius

`borderRadius`: `DEFAULT` 2px, `lg` 4px, `xl` 8px, `full` 9999px → set `RadiusTopLeft`/`TopRight`/
`BottomLeft`/`BottomRight` on the control (or `RadiusX`/`RadiusY` where supported). `rounded-full` on a
square avatar → radius = half the side to get a circle.
