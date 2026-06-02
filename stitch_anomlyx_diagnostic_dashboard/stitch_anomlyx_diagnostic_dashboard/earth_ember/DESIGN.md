---
name: Earth & Ember
colors:
  surface: '#18120d'
  surface-dim: '#18120d'
  surface-bright: '#3f3831'
  surface-container-lowest: '#120d08'
  surface-container-low: '#201b14'
  surface-container: '#241f18'
  surface-container-high: '#2f2922'
  surface-container-highest: '#3a342d'
  on-surface: '#ece0d6'
  on-surface-variant: '#dbc1b5'
  inverse-surface: '#ece0d6'
  inverse-on-surface: '#362f28'
  outline: '#a38c80'
  outline-variant: '#554339'
  surface-tint: '#ffb68e'
  primary: '#ffb68e'
  on-primary: '#542200'
  primary-container: '#d9773a'
  on-primary-container: '#491c00'
  inverse-primary: '#99460a'
  secondary: '#cfc5bd'
  on-secondary: '#352f2a'
  secondary-container: '#4c4640'
  on-secondary-container: '#bdb3ac'
  tertiary: '#ffb3b0'
  on-tertiary: '#5c181a'
  tertiary-container: '#d57573'
  on-tertiary-container: '#531114'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdbca'
  primary-fixed-dim: '#ffb68e'
  on-primary-fixed: '#331200'
  on-primary-fixed-variant: '#773300'
  secondary-fixed: '#ebe0d9'
  secondary-fixed-dim: '#cfc5bd'
  on-secondary-fixed: '#201b16'
  on-secondary-fixed-variant: '#4c4640'
  tertiary-fixed: '#ffdad8'
  tertiary-fixed-dim: '#ffb3b0'
  on-tertiary-fixed: '#3f0308'
  on-tertiary-fixed-variant: '#792e2f'
  background: '#18120d'
  on-background: '#ece0d6'
  surface-variant: '#3a342d'
typography:
  headline-lg:
    fontFamily: Eb Garamond
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
  headline-md:
    fontFamily: Eb Garamond
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
  body-lg:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Manrope
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Manrope
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.1px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin: 24px
---

# Earth & Ember Design System

## Brand & Style
Earth & Ember is a brand rooted in warmth, heritage, and modern craftsmanship. The personality is sophisticated yet grounded, evoking a sense of reliability and timeless quality. By moving to a dark color mode and adopting serif headlines, the brand shifts from a sterile corporate feel to a rich, editorial, and atmospheric experience. 

The design style is **Corporate / Modern** with a high-end editorial twist. It balances clean layouts with deep, resonant colors and refined typography to create an environment that feels premium and intentional. It targets an audience that values depth, clarity, and a quiet, confident aesthetic.

## Colors
The color palette is anchored in a dark mode environment, utilizing deep earth tones and warm embers. 

- **Primary (#c2652a):** A warm, burnt orange that serves as the "Ember," used for calls to action and key branding moments.
- **Secondary (#78706a):** A muted taupe-grey that provides a natural, stone-like balance to the warmth of the primary color.
- **Tertiary (#8c3c3c):** A deep clay red used for subtle accents and to add variety to the warm spectrum.
- **Neutral (#605850):** A warm, dark grey that forms the foundation of the interface, ensuring the dark mode feels organic rather than cold.

The "Fidelity" variant ensures that the generated tonal palettes remain true to these specific hues, maintaining a high-contrast and legible experience against the dark background.

## Typography
The typography strategy creates a tension between classic heritage and modern utility. 

- **Headlines:** Uses **EB Garamond**, a classic serif that brings an editorial authority and elegance to the interface. Headlines should be set with generous line height to allow the letterforms to breathe.
- **Body & Labels:** Uses **Manrope**, a modern geometric sans-serif. Manrope offers excellent legibility at smaller sizes and provides a functional, clean counterpoint to the decorative nature of the serif headlines.

On mobile devices, headlines should scale appropriately to ensure readability without excessive wrapping.

## Layout & Spacing
The layout follows a **fluid grid** system based on an 8px spacing rhythm. This ensures a consistent vertical and horizontal cadence throughout the application.

- **Desktop:** A 12-column grid with 24px margins and 16px gutters.
- **Tablet:** An 8-column grid with 24px margins and 16px gutters.
- **Mobile:** A 4-column grid with 16px margins and 12px gutters.

Spacing is used to create clear groupings of information. Larger gaps (24px+) are used between sections, while tighter spacing (8px-16px) is used for internal component layout.

## Elevation & Depth
In this dark-themed system, depth is conveyed through **tonal layers** rather than heavy shadows. Surfaces closer to the user are rendered in lighter shades of the neutral palette.

- **Background:** The deepest neutral shade.
- **Surface-Low:** Used for cards and secondary containers.
- **Surface-High:** Used for modals and elevated elements.

Low-opacity borders (1px, 10-15% opacity) are used to define boundaries between elements of similar tonal values, maintaining a clean and modern appearance without excessive visual noise.

## Shapes
The shape language is defined by a **Rounded** aesthetic. This softens the high-contrast dark mode and makes the interface feel more approachable and organic.

- **Standard Elements:** 0.5rem (8px) corner radius for buttons and input fields.
- **Large Containers:** 1rem (16px) corner radius for main content areas and large cards.
- **Full Rounding:** Pill shapes are reserved for tags, chips, and specific toggle states.

## Components
- **Buttons:** Primary buttons use the Ember (#c2652a) background with light text. Secondary buttons use an outlined style with the secondary color.
- **Input Fields:** Dark backgrounds with a subtle neutral border. Focus states use the primary color border to provide a "glow" effect.
- **Cards:** Use Surface-Low tonal layering with generous padding and 1rem corner radius.
- **Chips:** Highly rounded (pill-shaped) with subtle background fills to distinguish them from actionable buttons.
- **Lists:** Clean dividers using low-opacity neutral colors to separate line items without breaking the visual flow.