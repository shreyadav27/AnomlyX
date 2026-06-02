---
name: AnomalyX
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#9d4300'
  on-secondary: '#ffffff'
  secondary-container: '#fd761a'
  on-secondary-container: '#5c2400'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#0d1c2f'
  on-tertiary-container: '#76859b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#ffdbca'
  secondary-fixed-dim: '#ffb690'
  on-secondary-fixed: '#341100'
  on-secondary-fixed-variant: '#783200'
  tertiary-fixed: '#d5e3fd'
  tertiary-fixed-dim: '#b9c7e0'
  on-tertiary-fixed: '#0d1c2f'
  on-tertiary-fixed-variant: '#3a485c'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style
The brand personality is grounded in engineering precision and industrial reliability. It targets quality assurance engineers and floor managers who require immediate, unambiguous data interpretation. The visual style is **Corporate / Modern** with a lean toward **Minimalism**, prioritizing utility over decoration. 

The UI must evoke a sense of "digital instrumentation"—feeling as robust and dependable as the hardware it monitors. This is achieved through high-density data layouts, a restrained color palette, and clear visual hierarchy. Every element exists to facilitate the diagnostic workflow, reducing cognitive load during high-stakes inspections.

## Colors
The palette is rooted in industrial materials. The primary color is a deep Slate/Steel Blue (`#0F172A`), used for core navigation and text to provide a stable foundation. The secondary color is an Industrial Orange (`#F97316`), reserved strictly for primary actions, critical alerts, and diagnostic highlights to ensure they pierce through the neutral background.

Tertiary and Neutral colors are derived from a cold gray scale, mimicking brushed metal and concrete environments. 
- **Surface:** Light gray tints (`#F8FAFC`) are used for the main canvas.
- **Stroke/Dividers:** Mid-tone slates (`#E2E8F0`) provide subtle structural definition.
- **Success/Warning:** Standard semantic green and amber are used, but desaturated to maintain the professional aesthetic.

## Typography
The system utilizes **Inter** for all primary interface elements due to its exceptional legibility in data-dense environments and its neutral, modern character. Headlines use a tighter letter-spacing and heavier weights to establish a clear hierarchy.

**JetBrains Mono** is introduced as a secondary label font. This monospaced typeface is used for technical readouts, serial numbers, timestamps, and diagnostic coordinates, reinforcing the technical and precise nature of the platform. All typography scales are based on a 4px baseline grid to ensure vertical rhythm.

## Layout & Spacing
The layout follows a **Fixed Grid** approach for data dashboards to ensure consistency in component placement, transitioning to a **Fluid Grid** for inspection galleries. 

- **Desktop (1440px+):** 12-column grid with 32px margins and 16px gutters.
- **Tablet (768px - 1439px):** 8-column grid with 24px margins.
- **Mobile (Up to 767px):** 4-column grid with 16px margins.

Spacing is strictly mathematical, using multiples of 4px. Use `lg` (24px) for padding within major card containers and `sm` (8px) for internal component spacing (e.g., icon to text).

## Elevation & Depth
This design system uses **Tonal Layers** and **Low-Contrast Outlines** rather than aggressive shadows. This maintains a "flat-mechanical" feel.

- **Level 0 (Background):** `#F8FAFC` - The base work surface.
- **Level 1 (Cards/Sections):** White background with a 1px border (`#E2E8F0`). No shadow.
- **Level 2 (Dropdowns/Modals):** White background with a subtle, diffused shadow (Offset: 0, 4px; Blur: 12px; Color: `rgba(15, 23, 42, 0.08)`).
- **Active State:** Elements being interacted with should use a 2px inset border or a subtle tonal shift to `#F1F5F9`.

## Shapes
The design system employs a consistent **8px (0.5rem)** corner radius for most UI components (cards, buttons, input fields). This "Rounded" setting provides a professional, modern look that is approachable but remains disciplined and structured. 

Small utility elements like tags or status indicators may use a slightly smaller radius (4px) to maintain visual balance when nested inside larger 8px containers.

## Components
- **Buttons:** Primary buttons use the Industrial Orange background with white text. Secondary buttons use a Slate stroke with no fill. All buttons use 14px Medium weight text.
- **Input Fields:** Use a 1px Slate border. On focus, the border shifts to Primary Slate with a subtle 2px outer "glow" in a transparent primary tint.
- **Chips/Status:** Use a "dot" indicator next to the label. Defects are marked with a Red dot, while healthy components use a Green dot. Labels are set in JetBrains Mono.
- **Data Tables:** High-density with 1px horizontal dividers only. Header cells have a light gray background (`#F1F5F9`) to distinguish from data rows.
- **Diagnostic Cards:** Large-format containers for X-ray or thermal imagery. Imagery should be framed by an 8px border and include a monospaced "Coordinate Overlay" in the corners.
- **Checkboxes:** Square with a 2px radius, using Primary Slate for the checked state to maintain a serious, industrial tone.