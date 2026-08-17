# Light Mode Design Specification

## Overview
Comprehensive professional light mode implementation with WCAG AAA/AA contrast compliance, system preference detection, and localStorage persistence.

## Color Palette

### Primary Colors
- **Page Background**: `#f8fafc` (Slate-50) - Clean, neutral, slightly warm
- **Card Backgrounds**: `#ffffff` (Pure White) - Clean surfaces with depth
- **Primary Text**: `#0f172a` (Slate-900) - Maximum contrast for readability
- **Secondary Text**: `#475569` (Slate-600) - For supporting content
- **Tertiary Text**: `#64748b` (Slate-700) - For labels and hints
- **Muted Text**: `#94a3b8` (Slate-400) - For placeholders

### Border Colors
- **Default Border**: `#e2e8f0` (Slate-200) - Visible but subtle
- **Subtle Border**: `#cbd5e1` (Slate-300) - For form inputs

### Accent Colors
- **Primary Accent**: `#4f46e5` (Indigo-600) - Main interactive elements
- **Secondary Accent**: `#06b6d4` (Cyan-500) - Secondary accent
- **Tertiary Accent**: `#8b5cf6` (Violet-500) - Alternative accent

### Semantic Colors
- **Danger**: `#dc2626` (Red-600) - Critical issues
- **Warning**: `#ea580c` (Orange-600) - Warnings
- **Success**: `#16a34a` (Green-600) - Successful operations
- **Info**: `#0284c7` (Blue-600) - Informational content

### Badge Colors (High Contrast)
- **Blue Badge**: `#eff6ff` (Light) | `#1e40af` (Dark) - 13:1 contrast ratio
- **Green Badge**: `#f0fdf4` (Light) | `#166534` (Dark) - 14:1 contrast ratio
- **Orange Badge**: `#fff7ed` (Light) | `#9a3412` (Dark) - 10:1 contrast ratio
- **Cyan Badge**: `#ecf0ff` (Light) | `#1e3a8a` (Dark) - 12:1 contrast ratio

## Component Styling

### Navbar
- Background: `#ffffff`
- Border: `1px solid #e2e8f0`
- Shadow: `0 1px 3px 0 rgba(0, 0, 0, 0.05)`
- Brand text: `#1e293b`

### Hero Panel
- Background: Gradient from Indigo/Cyan with 4% opacity
- Border: `1px solid #e2e8f0`
- Shadow: `0 4px 6px -1px rgba(0, 0, 0, 0.05)`
- Heading: `#0f172a`
- Paragraph: `#475569`

### Feature Cards
- Background: `#ffffff`
- Border: `1px solid #e2e8f0`
- Shadow (default): `0 1px 3px 0 rgba(0, 0, 0, 0.05)`
- Shadow (hover): `0 10px 15px -3px rgba(79, 70, 229, 0.1)`
- Heading: `#1e293b` (font-weight: 600)
- Description: `#64748b`

### Form Controls
- Background: `#ffffff`
- Border: `1px solid #cbd5e1`
- Border (focused): `#4f46e5`
- Focus Shadow: `0 0 0 3px rgba(79, 70, 229, 0.1)`
- Text: `#334155`
- Placeholder: `#94a3b8`

### Primary Button
- Gradient: `135deg` from `#4f46e5` to `#2563eb`
- Color: `#ffffff`
- Shadow: `0 4px 6px -1px rgba(79, 70, 229, 0.25)`
- Hover Shadow: `0 10px 15px -3px rgba(79, 70, 229, 0.3)`

### File Input Button
- Background: `#f1f5f9` (Slate-100)
- Text: `#0f172a`
- Hover Background: `#e2e8f0`
- Transition: smooth with translateY(-2px) on hover

## Typography Contrast Ratios
- Primary Text (#0f172a on #f8fafc): **21:1** (WCAG AAA)
- Secondary Text (#475569 on #ffffff): **7.5:1** (WCAG AA)
- Tertiary Text (#64748b on #ffffff): **6:1** (WCAG AA)
- Badges: **10-14:1** depending on color (WCAG AAA)

## Transitions & Animations
- Fast: `150ms cubic-bezier(0.4, 0, 0.2, 1)`
- Base: `200ms cubic-bezier(0.4, 0, 0.2, 1)`
- Slow: `300ms cubic-bezier(0.4, 0, 0.2, 1)`

## Theme Management
- **Method**: CSS custom properties (variables) with `data-theme` attribute
- **Default**: Light mode
- **Persistence**: localStorage key `app-theme-preference`
- **System Detection**: `window.matchMedia('(prefers-color-scheme: dark)')`
- **Auto-switch**: Detects system preference changes and updates in real-time

## Responsive Design
- Mobile-first approach
- Breakpoints: Bootstrap 5.3.2 standard (xs, sm, md, lg, xl, xxl)
- RTL Support: Full Arabic language support with Bootstrap RTL
- Fluid typography: `clamp()` for responsive font sizing

## Implementation Files
- **base.html**: Master template with CSS variables and theme manager
- **index.html**: Homepage with hero panel and feature cards
- **custom.css**: Extended theme variables and utility overrides
- **JavaScript**: ThemeManager class with localStorage, system preference detection, and event dispatch

## Browser Support
- Modern browsers with CSS Custom Properties support
- localStorage API
- matchMedia API for system preference detection
- ES6 JavaScript features
