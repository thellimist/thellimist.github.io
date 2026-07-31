---
summary: "Shared tier-board component used by the Anime and Chocolate pages."
read_when:
  - "Changing tier rows, rails, cards, counts, filters, responsive behavior, or tooltips."
  - "Adding another tier-list page to the site."
---

# Tier-list component

Anime and Chocolate share one presentation and rendering layer:

- `stylesheets/tier-list.css` owns the page shell, S-D board, colored rails,
  counts, cards, cover treatment, notes, badges, responsive layout, filter
  control shell, and tooltip base.
- `javascripts/tier-list.js` exposes `window.TierList`.

## Renderer

`TierList.render` receives:

- `root` - board element.
- `tiers` - ordered `{ key, label, description? }` definitions. A description
  makes the tier rail keyboard-focusable and exposes the text to page-owned
  tooltip behavior.
- `items` - page-specific data.
- `getTier(item)` - returns the item's tier key.
- `createCard(item)` - returns a page-specific card element.
- `idPrefix` - keeps accessible row IDs unique.
- `emptyMessage` - string or function for empty rows.

`TierList.createCard` builds the shared cover, optional score badge, optional
note, and title. Use the `tier-card--product` modifier for product photography
that must use `object-fit: contain`.

`TierList.positionTooltip` positions page-specific tooltip content around its
card without clipping the viewport.

## Page extensions

- Anime owns Supabase reads, average scoring, search, vote details, comments,
  and its tier-description tooltips.
- Chocolate owns JSON loading, country/brand filters, product metadata, and Maps
  links. It also uses tier descriptions for the S-D letter tooltips.

Use `.tier-filters`, `.tier-filter`, and `.tier-filter-control` for filter
layout, labels, and closed controls. Add `.tier-filter-control--choice` to
select-like controls that need the shared arrow and padding.

Do not duplicate tier rows, card-shell CSS, or filter-control CSS inside a page.
Add page-specific controls before the shared `.tier-board` and keep their logic
in the page's own script.
