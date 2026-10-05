---
name: "Atlas Admin"
description: "An enterprise admin tool that respects density. Cool bone-grey surfaces, Inter for prose and IBM Plex Mono with tabular numerals for every figure, a single steel-blue accent reserved for the active module pane border. Built for B2B internal tools, ops dashboards, and admin consoles where information density is the feature, not the bug."
tags: [enterprise, admin, dashboard, minimal, saas]
colors:
  primary:   "#0f1419"
  secondary: "#5a626c"
  tertiary:  "#0f1419"
  neutral:   "#e6e9ed"
  surface:   "#f1f3f6"
typography:
  display: Inter
  body:    Inter
  mono:    "IBM Plex Mono"
  scale:
    hero: "2.75rem / 1.08 / 700 / -0.025em"
    h1:   "1.875rem / 1.18 / 600 / -0.018em"
    h2:   "1.25rem / 1.3 / 600 / -0.012em"
    body: "0.875rem / 1.55 / 400 / 0"
radius:
  sm: 3px
  md: 5px
  lg: 7px
  pill: 9999px
shadows:
  card:   "rgba(15,20,25,0.04) 0 1px 2px"
  button: none
borders:
  card:    "1px solid rgba(15,20,25,0.08)"
  divider: rgba(15,20,25,0.08)
buttons:
  primary:
    background: #0f1419
    color: #f1f3f6
    border: none
    shape: rounded
    padding: 8px 16px
    font: 600 / 0.8125rem
  secondary:
    background: #ffffff
    color: #0f1419
    border: 1px solid rgba(15,20,25,0.14)
    shape: rounded
    padding: 8px 16px
    font: 500 / 0.8125rem
  outline:
    background: transparent
    color: #0f1419
    border: 1px solid rgba(15,20,25,0.18)
    shape: rounded
    padding: 8px 16px
    font: 500 / 0.8125rem
  ghost:
    background: transparent
    color: #5a626c
    border: none
    shape: rounded
    padding: 8px 12px
    font: 500 / 0.8125rem
charts:
  variant: "thin-bars"
  stroke_width: 1.25
  fill_opacity: 0.05
  gridlines: true
  bar_gap: 6px
  highlight: single
  dot_marker: false
fonts_url: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
dependencies: ["lucide-react"]
---

# Atlas Admin

## How ResearchForge applies this system

`src/researchforge/web/static/style.css` declares every token below once in `:root`.
Project-specific decisions, recorded so later changes stay consistent:

- **Fonts are self-hosted** from `web/static/fonts/` instead of the Google Fonts link,
  because ResearchForge runs locally and must work offline.
- **Statement kinds** keep their margin-rule shapes and map onto the palette:
  evidence = success, solid; inference = Ink 60, dashed; hypothesis = warn, dotted;
  experimental result = Ink, double. Rejected claims and the critique use error.
- **Steel** appears only on the active module pane (the investigation sheet's left
  border), the active sidebar step, the focus ring, and the active boxed tab.
- **Density:** the landing page uses the `spacious` density mode (1rem body); the
  investigation view uses the default 14px body.
- **Dark mode** is not defined by Atlas. It is derived from the same palette with
  `color-mix()`, so it adds no new hues.
- The `lucide-react` dependency does not apply: the UI is vanilla HTML/JS with no icon set.

## AI Build Instructions

> **Read this section before writing any code.** The rules below
> are non-negotiable. Every value used in the UI must come from this
> file's frontmatter — never substitute, approximate, or invent new
> colors, fonts, radii, or shadows. If a value is missing, ask the
> user before adding one.

### 1 · Your role

You are building UI for a project that has adopted **Atlas Admin** as its
design system. Treat `DESIGN.md` as the single source of truth.
Your job is to translate the user's product requirements into
components and pages that look like they were designed by the same
person who authored this file.

### 2 · Token compliance

- Pull every color, font family, radius, shadow, and spacing value
  from the frontmatter at the top of this file.
- Use semantic roles (e.g. `primary`, `accent`, `muted`) — never
  hard-code hex values that bypass the system.
- When a token can be expressed as a CSS variable, declare it once
  in your global stylesheet and reference it everywhere downstream.
- The Google Fonts `<link>` is provided in the Typography section.
  Add it to `<head>` before any component renders.

### 3 · Component recipes

Use these recipes verbatim when building the corresponding component.

#### Buttons

Four variants are defined. Pick one — never blend variants or invent a fifth.

- **Primary** — rounded shape, bg `#0f1419`, text `#f1f3f6`, padding `8px 16px`, weight `600`.
- **Secondary** — rounded shape, bg `#ffffff`, text `#0f1419`, border `1px solid rgba(15,20,25,0.14)`, padding `8px 16px`, weight `500`.
- **Outline** — rounded shape, text `#0f1419`, border `1px solid rgba(15,20,25,0.18)`, padding `8px 16px`, weight `500`.
- **Ghost** — rounded shape, text `#5a626c`, padding `8px 12px`, weight `500`.

Reach for **primary** as the single dominant CTA per screen.
**Secondary** for the supporting action. **Outline** for tertiary
actions in toolbars. **Ghost** for inline links and table actions.

#### Cards

- Background: `#f1f3f6`
- Border: `1px solid rgba(15,20,25,0.08)`
- Shadow: `rgba(15,20,25,0.04) 0 1px 2px`
- Radius: `radius.lg` (`7px`)
- Internal padding: `20px` for compact cards, `24–28px` for content cards.

#### Tabs

Variant: `boxed`. Each tab is a bordered card. Active tab gets the accent border and a subtle fill.

#### Charts

- Bar/line variant: `thin-bars`
- Highlight strategy: `single` — emphasize a single bar/point per chart.

#### Typography pairings

- **Display (`Inter`)** — h1, h2, hero headlines, brand wordmarks.
- **Body (`Inter`)** — paragraphs, labels, button text, form inputs.
- **Mono (`IBM Plex Mono`)** — code, eyebrows, metadata, numerals in tables.

### 4 · Hard constraints

Never do any of the following without explicit instruction from the user:

- Introduce a new color, font, radius, or shadow that isn't declared above.
- Mix this system with another (e.g. don't paste in Material or Bootstrap defaults).
- Use generic gradient defaults (purple→blue, peach→pink) — they break the system's voice.
- Reach for emoji icons. Use a consistent icon library and size icons in line with body type.
- Add motion that exceeds the system's restraint — keep transitions short (≤200ms) and subtle.

### 5 · Before you finish — verify

Run through this checklist for every screen you produce:

- [ ] Every color used appears in the Colors table above.
- [ ] Headlines use the display font; body copy uses the body font.
- [ ] Buttons match one of the declared variants exactly (shape, padding, weight).
- [ ] Border-radius values come from `radius.sm` / `radius.md` / `radius.lg` / `radius.pill`.
- [ ] Cards and dividers use the declared border + shadow tokens.
- [ ] No values were invented; if you needed something missing, you stopped and asked.

---

## 1. Atmosphere

Atlas Admin is an enterprise admin tool that respects density. The page surface is cool bone-grey `#f1f3f6` with cards lifted to pure white — every surface differing by 1-2% lightness. Inter handles prose at the small body size (14px) that admin consoles actually need to fit dense data; IBM Plex Mono with tabular numerals carries every ID, count, percentage, timestamp. Chrome is hairlines at 8% ink. The single accent is muted steel-blue `#3a5a7e` that appears only on the active module pane left border, the active sidebar item, and the focus ring. Status colors (success/warn/error) are reserved for actual status — never for UI accents.

The discipline is in the density: 14px body so an ops table actually fits a screen, mono numerals for column alignment, and one steel-blue that reads as "you are here" without ever shouting.

**Signature moves**
- 14px body in Inter — admin consoles need density, not marketing spacing
- IBM Plex Mono with `font-variant-numeric: tabular-nums` on every ID, count, timestamp, percentage
- Steel-blue `#3a5a7e` only on active module pane border + active sidebar item + focus ring
- Boxed tabs (5px radius, 1px hairline) — the tmux-pane voice for module switching
- Cool bone-grey `#f1f3f6` page → pure white card — tonal-shift, no shadow drama

## 2. Palette

### Surfaces
- **Bone Grey** `#f1f3f6` — page background (cool fine off-white)
- **Card** `#ffffff` — elevated surface, primary card
- **Header** `#e6e9ed` — table headers, sidebar background

### Ink
- **Ink** `#0f1419` — text, headings, primary CTA fill (cool near-black, slight blue undertone)
- **Ink 60** `#5a626c` — secondary text, mono labels
- **Hairline** `rgba(15,20,25,0.08)` — every divider, every card edge

### Accent
- **Steel** `#3a5a7e` — active module pane border, active sidebar item, focus ring
- **Steel Soft** `rgba(58,90,126,0.10)` — hovered sidebar item, focus ring background

### Status (semantic only — never UI accent)
- Success `#1f7a4d` · Warn `#b3801f` · Error `#a3331f` — used only on actual status badges

## 3. Typography

| Role | Font | Size | Weight | Leading | Tracking |
|------|------|------|--------|---------|----------|
| Hero | Inter | 44px | 700 | 1.08 | -0.025em |
| H1 / Page Title | Inter | 30px | 600 | 1.18 | -0.018em |
| H2 / Section | Inter | 20px | 600 | 1.3 | -0.012em |
| Body | Inter | 14px | 400 | 1.55 | 0 |
| UI / Button | Inter | 13px | 500 | 1.4 | 0 |
| ID / Count / Metric | IBM Plex Mono | 13px | 500 | 1.0 | 0 tabular-nums |
| Label | IBM Plex Mono | 11px | 500 | 1.0 | 0.06em uppercase |
| Timestamp | IBM Plex Mono | 12px | 500 | 1.0 | 0 tabular-nums |
| Big KPI | IBM Plex Mono | 24px | 600 | 1.0 | 0 tabular-nums |

The 14px body is deliberately small — admin consoles must fit dense tables. Plex Mono for every numeric or ID string keeps columns pixel-aligned.

## 4. Buttons

### Primary (Ink Compact)
```css
background: #0f1419;
color: #f1f3f6;
padding: 8px 16px;
border-radius: 5px;
font-weight: 600;
```

The 8px vertical padding is tight on purpose — admin actions live in toolbars and table rows where height matters.

### Secondary (Card White)
- Pure white, 1px hairline at 14% ink, ink text — same compact size

### Outline & Ghost
- Outline: transparent, 1px hairline at 18% ink
- Ghost: no border, ink-60, hover lifts to ink

## 5. Cards

```css
background: #ffffff;
border: 1px solid rgba(15,20,25,0.08);
border-radius: 7px;
box-shadow: rgba(15,20,25,0.04) 0 1px 2px;
```

The single 1px shadow is the maximum lift. The active module pane adds a 2px steel left border — the "you are here" indicator, borrowed from a tmux/zellij active pane.

## 6. Charts

Thin precise bars (3px wide, 6px gap) with dashed gridlines at 8% ink — used for daily-throughput and queue-depth charts. One bar in steel, others in 22% ink. Line charts at 1.25px ink with a 5% steel fill. Y-axis labels in IBM Plex Mono uppercase 11px aligned to the right.

## 7. Tabs

Boxed tabs with 5px radius and 1px hairline at 8% ink. Active = white background, 1px steel border, ink text. Inactive = transparent, ink-60. Reads like a tmux pane selector — module switching, not nav.

## 8. Spacing

- Base 4px (table-row aware)
- Scale: `4, 8, 12, 16, 20, 24, 32, 40, 56, 80`
- Section padding: 56px desktop, 24px mobile — admin density

## 9. Do's & don'ts

✅ **Do**
- Use 14px body — admin consoles need density, not marketing spacing
- Use IBM Plex Mono with tabular-nums on every ID, count, percentage, timestamp
- Reserve steel for active module pane border + active sidebar item + focus ring
- Hold status colors (success/warn/error) to actual status badges only — never as UI accent

❌ **Don't**
- Use 16px+ body — admin tables become wasteful and require more scroll
- Use a second UI accent — steel alone, on three specific surfaces
- Use bright color for status — muted versions only (success `#1f7a4d`, never `#22c55e`)
- Add card shadows beyond the 1px lift — the cool tonal step is the only depth

---

## Tokens

> Generated from the same source the live preview renders from.
> Treat the values below as the contract — never substitute approximations.

### Colors

| Role      | Value |
|-----------|-------|
| primary   | `#0f1419` |
| secondary | `#5a626c` |
| tertiary  | `#0f1419` |
| neutral   | `#e6e9ed` |
| surface   | `#f1f3f6` |

### Typography

- **Display:** Inter
- **Body:** Inter
- **Mono:** IBM Plex Mono

| Role | size / leading / weight / tracking |
|------|------------------------------------|
| Hero | 2.75rem / 1.08 / 700 / -0.025em |
| H1   | 1.875rem / 1.18 / 600 / -0.018em |
| H2   | 1.25rem / 1.3 / 600 / -0.012em |
| Body | 0.875rem / 1.55 / 400 / 0 |

### Radius

- sm: `3px`
- md: `5px`
- lg: `7px`
- pill: `9999px`

### Shadows

- **card:** `rgba(15,20,25,0.04) 0 1px 2px`
- **button:** `none`

### Borders

- **card:** `1px solid rgba(15,20,25,0.08)`
- **divider:** `rgba(15,20,25,0.08)`

### Buttons

Four variants, each fully tokenized. The preview renders from these exact values.

#### Primary

| Property | Value |
|----------|-------|
| shape | `rounded` |
| background | `#0f1419` |
| color | `#f1f3f6` |
| border | `none` |
| padding | `8px 16px` |
| fontWeight | `600` |
| fontSize | `0.8125rem` |

#### Secondary

| Property | Value |
|----------|-------|
| shape | `rounded` |
| background | `#ffffff` |
| color | `#0f1419` |
| border | `1px solid rgba(15,20,25,0.14)` |
| padding | `8px 16px` |
| fontWeight | `500` |
| fontSize | `0.8125rem` |

#### Outline

| Property | Value |
|----------|-------|
| shape | `rounded` |
| background | `transparent` |
| color | `#0f1419` |
| border | `1px solid rgba(15,20,25,0.18)` |
| padding | `8px 16px` |
| fontWeight | `500` |
| fontSize | `0.8125rem` |

#### Ghost

| Property | Value |
|----------|-------|
| shape | `rounded` |
| background | `transparent` |
| color | `#5a626c` |
| border | `none` |
| padding | `8px 12px` |
| fontWeight | `500` |
| fontSize | `0.8125rem` |

### Charts

| Property | Value |
|----------|-------|
| variant | `thin-bars` |
| strokeWidth | `1.25` |
| fillOpacity | `0.05` |
| gridlines | `true` |
| barGap | `6px` |
| highlight | `single` |
| dotMarker | `false` |

---

## Pro tokens

> Production-fidelity tokens. States, density, motion, elevation,
> content rules and a measured WCAG contract — derived from the
> resting tokens unless explicitly authored.

### States

#### Button

- **hover** — shadow: `0 4px 12px -2px rgba(15,23,42,0.18)`, filter: `brightness(0.97)`
- **focus** — outline: `2px solid rgba(15, 20, 25, 0.5)`, outline-offset: `2px`
- **active** — shadow: `0 1px 2px rgba(15,23,42,0.1)`, transform: `scale(0.98)`
- **disabled** — opacity: `0.4`, filter: `saturate(0.5)`
- **loading** — opacity: `0.7`
- **selected** — bg: `#0f1419`, color: `#f1f3f6`

#### Input

- **hover** — border: `1px solid rgba(15, 20, 25, 0.5)`
- **focus** — border: `1.5px solid #0f1419`, shadow: `0 0 0 4px rgba(15, 20, 25, 0.15)`
- **disabled** — bg: `rgba(15, 20, 25, 0.04)`, opacity: `0.4`
- **error** — border: `1.5px solid #DC2626`, shadow: `0 0 0 4px rgba(220,38,38,0.15)`

#### Card

- **hover** — shadow: `0 12px 28px -12px rgba(15,23,42,0.18)`, transform: `translateY(-2px)`
- **selected** — bg: `rgba(15, 20, 25, 0.04)`, border: `1.5px solid #0f1419`
- **dragging** — shadow: `0 20px 48px -16px rgba(15,23,42,0.3)`, transform: `scale(1.02) rotate(-0.5deg)`, opacity: `0.9`

#### Tab

- **hover** — bg: `rgba(15, 20, 25, 0.06)`, color: `#0f1419`
- **focus** — outline: `2px solid rgba(15, 20, 25, 0.5)`, outline-offset: `2px`
- **selected** — color: `#0f1419`, border: `0 0 2px 0 solid #0f1419`

### Density

| Mode | padding × | row × | body | radius × | Use for |
|------|-----------|-------|------|----------|---------|
| compact | 0.72 | 0.78 | 0.8125rem | 0.85 | Information-dense — tables, IDEs, dashboards |
| comfortable | 1 | 1 | 0.9375rem | — | Default — most product UI |
| spacious | 1.35 | 1.3 | 1rem | 1.15 | Editorial — marketing, long-form, settings |

### Motion

**Signature — Quiet ease.** 240 ms ease-out for all standard transitions. Reliable, invisible — motion stays out of the way.

```css
transition: all 240ms cubic-bezier(0.4, 0, 0.2, 1);
```

| Token | Value |
|-------|-------|
| duration.instant | `80ms` |
| duration.fast | `160ms` |
| duration.base | `240ms` |
| duration.slow | `380ms` |
| easing.standard | `cubic-bezier(0.4, 0, 0.2, 1)` |
| easing.decelerate | `cubic-bezier(0.0, 0, 0.2, 1)` |
| easing.accelerate | `cubic-bezier(0.4, 0, 1, 1)` |
| easing.spring | `cubic-bezier(0.34, 1.4, 0.64, 1)` |

### Elevation

Five-level scale, system-specific recipe.

| Level | Shadow | Recipe |
|-------|--------|--------|
| level0 | `none` | Flat — hairline border separates. |
| level1 | `0 1px 2px rgba(15,23,42,0.06), 0 1px 3px rgba(15,23,42,0.04)` | List rows, resting cards. |
| level2 | `0 4px 12px -2px rgba(15,23,42,0.1), 0 2px 6px rgba(15,23,42,0.06)` | Hover cards, popover. |
| level3 | `0 12px 32px -8px rgba(15,23,42,0.16), 0 4px 12px rgba(15,23,42,0.08)` | Sheets, side panels. |
| level4 | `0 28px 64px -16px rgba(15,23,42,0.28), 0 8px 24px rgba(15,23,42,0.12)` | Modals — scrim required. |

### Content

- **measure:** `68ch` (max line length for body prose)
- **paragraph spacing:** `1.2em`
- **list indent:** `1.5em`
- **list gap:** `0.5em`
- **link:** color `#0f1419`, underline `hover`
- **blockquote:** border `3px solid rgba(15, 20, 25, 0.6)`, padding `0.5em 0 0.5em 1.25em`
- **code:** background `rgba(15, 20, 25, 0.06)`, color `#0f1419`

### Accessibility (WCAG 2.1)

**Overall:** AA

| Pair | Ratio | Required | Grade | Suggested fix |
|------|-------|----------|-------|---------------|
| Body text on surface | 16.65:1 | AA | AAA | — |
| Body text on canvas | 15.2:1 | AA | AAA | — |
| Muted text on surface | 5.56:1 | AA | AA | — |
| Accent on surface | 16.65:1 | AA-Large | AAA | — |
| Accent on canvas | 15.2:1 | AA-Large | AAA | — |
