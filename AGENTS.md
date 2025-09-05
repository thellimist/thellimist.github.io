# Custom CSS Documentation for Agents

This document explains the custom CSS classes and styles available in the blog template that agents can use when creating or editing posts.

## Available Custom CSS Classes

### Spoiler Tags
**Class:** `.spoiler`
**Usage:** `<span class="spoiler">Hidden text here</span>`
**Description:** Creates Discord/Reddit-style hidden text that reveals on hover
**Styling:** 
- Light gray background that matches text color (hidden by default)
- Rounded corners with padding
- Smooth transition animation
- Reveals dark text on hover

**Example:**
```markdown
- <span class="spoiler">This text is hidden until you hover over it</span>
```

### Collapsible Details
**Elements:** `<details>` and `<summary>`
**Usage:** Built into HTML, styled with CSS
**Description:** Creates expandable/collapsible sections
**Styling:**
- Triangle arrows that rotate when opened
- Proper spacing and margins
- Consistent with theme colors

**Example:**
```markdown
<details>
<summary>Click to expand</summary>
This content is hidden by default and expands when clicked.
</details>
```

## Theme System

The site uses CSS custom properties (variables) for theming:

### Light Theme (Default)
- `--bg: #fff` - Background color
- `--text-primary: #222` - Primary text color
- `--text-muted: #555` - Muted text color
- `--accent: #2563eb` - Accent/link color
- `--border: #e2e2e2` - Border color
- `--card-bg: #f9f9f9` - Card background color

### Dark Theme
Available via `.dark-theme` class with adjusted colors for dark mode.

## Typography

The site uses Inter font with optimized spacing and sizing:
- Base font size: 17px
- Line height: 1.55
- Letter spacing: -0.01em for headings

## When Creating Posts

1. **Use semantic HTML** when possible
2. **Leverage existing CSS classes** rather than inline styles
3. **Test spoiler tags** by using `<span class="spoiler">text</span>`
4. **Use details/summary** for expandable content
5. **Maintain consistency** with existing styling

## Adding New CSS

If you need new custom styles:
1. Add them to `/stylesheets/styles.css`
2. Use CSS custom properties where appropriate
3. Document the new styles in this file
4. Consider both light and dark theme compatibility

## File Locations

- Main stylesheet: `/stylesheets/styles.css`
- This documentation: `/AGENTS.md`
- Posts directory: `/_posts/`

## Best Practices

1. **Avoid inline styles** - Use CSS classes instead
2. **Test responsiveness** - Ensure styles work on mobile
3. **Consider accessibility** - Ensure sufficient color contrast
4. **Use semantic HTML** - Helps with SEO and accessibility
5. **Follow existing patterns** - Maintain visual consistency