# Financial Board Design Authenticity Standard

## Purpose

Financial Board should look like a deliberately designed market workstation, not a generic generated SaaS dashboard. This standard applies to every visible UI change.

No single visual pattern proves that a site was produced by Codex or any other tool. In particular, a green status dot is a common interface convention, not a Codex signature. IBM Carbon documents dot badges as a general status-indicator variant and warns that status must not rely on color alone. We still avoid decorative live dots because they add little information here and have become associated with generic generated dashboards.

The useful test is pattern density: several default choices appearing together make an interface feel unconsidered. Public critiques repeatedly call out generic typography, neon-on-dark palettes, excessive rounded cards, pill labels, identical component grids, repetitive spacing, canned copy, and motion without purpose.

## Current dashboard audit

Audit state: Overview, 1280 × 720, dark theme, live dashboard data.

Evidence captured locally during the audit:

- `/var/folders/pj/lyn662hd4v596l29kq7ztmjr0000gn/T/financial-board-ai-tells-audit/01-before.png`
- `/var/folders/pj/lyn662hd4v596l29kq7ztmjr0000gn/T/financial-board-ai-tells-audit/02-after.png`
- `/var/folders/pj/lyn662hd4v596l29kq7ztmjr0000gn/T/financial-board-ai-tells-audit/03-mobile.png`

Patterns found and corrected:

1. Decorative green dots were used for backend, live quote, dossier, and inline freshness states.
2. The headline ribbon used a generic boxed `LIVE` badge despite already showing current headlines.
3. Inter and JetBrains Mono created a familiar generated-dashboard typography pairing.
4. The first-open logo used the common fade-up-and-scale entrance.
5. The status bar repeated bordered label chips for information that works better as plain text.
6. Cyan was brighter than necessary against the dark interface.
7. Several source comments named an implementation tool instead of describing the product design layer.

## Required design rules

### Status and freshness

- Do not use a green dot, pulsing dot, glowing orb, or color-only mark to mean live, online, current, or healthy.
- Write the state in plain text: `Live`, `Updating`, `Delayed`, `Cached`, `Closed`, or a timestamp.
- Pair market color with a sign or label. Gains and losses may remain green/red because they are meaningful financial conventions, but color must not carry the meaning alone.
- Reserve bordered status labels for states that users must scan or act on. Do not decorate ordinary metadata as pills.

### Typography

- Use IBM Plex Sans for interface copy and IBM Plex Mono for prices, timestamps, symbols, and measurements.
- Keep a clear hierarchy through weight, size, and spacing. Do not make every heading, label, and value the same optical weight.
- Uppercase is allowed for established financial abbreviations such as `P/E`, `SMA`, `52W`, and exchange symbols. Do not use repeated tracked-uppercase eyebrow text as decoration.
- Avoid generic launch copy, buzzwords, aphoristic fragments, and excessive em dashes. Describe the data, source, risk, or action directly.

### Color

- Use the product palette: near-black surfaces, restrained amber brand accents, and steel blue for informational series.
- Use green, red, and yellow only for semantic market direction, success, error, and warning states.
- Do not use purple-to-blue gradients, gradient text, decorative neon glows, blurred color orbs, or arbitrary accent colors.
- If an accent could be swapped for any other color without changing meaning, remove it or return it to a neutral token.

### Surfaces and components

- Prefer flat groups, dividers, and alignment over nested cards.
- Default radii are 2 px, 3 px, and 4 px. Full pills are reserved for compact filters or genuine state tags.
- Do not pair a hairline border with a wide diffuse shadow.
- Avoid grids of identical icon-heading-copy cards. Component shape must follow the data or task.
- Keep controls compact and domain-specific. Do not add decorative icons, oversized icon tiles, fake illustrations, or placeholder imagery.

### Layout and spacing

- Use the market workflow to establish hierarchy: benchmarks, active instrument, scenario context, chart, then supporting detail.
- Related controls use tight spacing; separate analytical sections use larger spacing. Do not apply one gap value everywhere.
- Avoid generic centered heroes, symmetric three-card sections, vanity metrics, and large empty marketing areas.
- Preserve stable geometry during staged refreshes. Updating data must not shift the user’s reading position.

### Motion

- Motion must explain state change or continuity.
- Do not use repeated fade-up-on-scroll, hover scale, bounce, elastic motion, floating badges, pulsing status dots, or layout-property animation.
- The first-open brand moment may use a short opacity reveal only. It must remain one-time and respect reduced motion.

### Copy and provenance

- Use source labels, timestamps, confidence, unknowns, and fallback labels.
- Avoid claims such as `live` when the payload is cached or historical.
- UI copy must stand alone without mentioning prompts, models, generators, Codex, or implementation tools.
- Source comments should explain product intent or technical behavior, not the tool that wrote the code.

## Review checklist

Before merging a UI change:

- [ ] No decorative or color-only live indicator was added.
- [ ] No generic eyebrow badge, gradient headline, neon glow, or ornamental orb was added.
- [ ] No new nested-card layer exists where spacing or a divider would work.
- [ ] Pills are limited to filters or meaningful states.
- [ ] Copy names a market fact, source, uncertainty, or user action.
- [ ] Typography follows IBM Plex Sans/Mono and preserves measurable hierarchy.
- [ ] Green/red states also include a sign, word, icon, or value.
- [ ] Motion is functional, opacity/transform-based, and covered by reduced-motion behavior.
- [ ] Desktop and mobile screenshots were inspected for overflow, clipping, unstable refreshes, and repetitive visual rhythm.
- [ ] The browser console and automated UI contracts are clean.

## Research basis

- [Impeccable: Slop pattern catalog](https://impeccable.style/slop/) — catalog of recurring generated-UI patterns covering typography, color, cards, layout, motion, and copy.
- [Shuffle: Why Do Most AI-Generated Websites Look the Same?](https://shuffle.dev/blog/2026/01/why-do-most-ai-generated-websites-look-the-same/) — explains how underspecified work converges on common layouts and generic visual choices.
- [IBM Carbon: Status indicators](https://carbondesignsystem.com/patterns/status-indicator-pattern/) — establishes that dot indicators are a general UI convention and that accessible status requires more than color.
- [TechRadar Pro: Editing AI-generated websites](https://www.techradar.com/pro/website-building/the-ultimate-guide-to-editing-ai-generated-websites) — recommends replacing default elements with product-specific brand, content, hierarchy, and accessibility decisions.

These sources are heuristics, not provenance detectors. This project uses them to avoid default-looking design, not to make claims about how another website was built.
