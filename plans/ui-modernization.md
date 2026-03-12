# UI Modernization Plan

**Status:** Active
**Owner:** @frontend-agent
**Manager:** @pm-agent

## Overview
Transform the current "Raw HTML/Custom CSS" interface into a modern, responsive, card-based Design System. The goal is to improve maintainability (variables), usability (feedback), and aesthetics.

## Phase 1: Foundation (CSS Variables & Cleanup)
- [x] **CSS Audit:** Analyze `server_django/static/css/dashboard.css` to identify hardcoded colors and spacing.
- [x] **Define Design Tokens:** Create a `:root` block with CSS variables for:
    -   Colors: `--primary`, `--secondary`, `--bg-body`, `--bg-card`, `--text-main`, `--text-muted`.
    -   Spacing: `--spacing-sm`, `--spacing-md`, `--spacing-lg`.
    -   Borders: `--radius-sm`, `--radius-md`.
- [x] **Refactor Existing CSS:** Replace hardcoded values with new variables.

## Phase 2: Structural Upgrade (Layout)
- [x] **Grid System:** Refactor `dashboard.html` to use CSS Grid for the main layout instead of floats or simple flex.
- [x] **Card Component:** Create a standardized `.card` class with:
    -   Background color (`--bg-card`).
    -   Border radius (`--radius-md`).
    -   Subtle box-shadow.
    -   Padding (`--spacing-md`).
- [x] **Responsive Design:** Ensure the grid collapses correctly on mobile (<768px).

## Phase 3: Visual Polish & Interactions
- [x] **Micro-interactions:** Add hover effects to buttons and cards.
- [x] **Loading States:** Implement "Skeleton Screens" or spinners for charts before WebSocket data arrives.
- [x] **Navigation:** Style the sidebar/header to match the new theme.
- [x] **Dark Mode Prep:** Ensure all colors are mapped to variables so a `.dark-theme` class can override them easily.

## Dependencies
- Does not affect backend logic (`apps/`).
- Requires coordination with `dashboard-ui.js` if class names change significantly.
