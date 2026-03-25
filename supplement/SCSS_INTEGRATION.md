# Integrating Survey System Styles into Your Theme

## Overview

The survey system styles have been separated into SCSS partials that you can integrate into your existing `theme.scss` and `theme-dark.scss` files. This keeps your Quarto documents clean and maintainable.

---

## Files Provided

1. **`_survey-system.scss`** - Main styles for the survey system
2. **`_survey-system-dark.scss`** - Dark theme overrides
3. **`workflow-survey-system-clean.qmd`** - QMD file without embedded CSS

---

## Integration Steps

### Step 1: Add SCSS Partials to Your Project

Place the SCSS files in the same directory as your `theme.scss` and `theme-dark.scss` files (your root directory):

```
your-project/
├── theme.scss
├── theme-dark.scss
├── _survey-system.scss          ← Add this
├── _survey-system-dark.scss     ← Add this
└── workflow-survey-system-clean.qmd
```

### Step 2: Import into `theme.scss`

At the **end** of your `theme.scss` file, add:

```scss
// ==============================================================================
// INTERACTIVE WORKFLOW SURVEY SYSTEM
// ==============================================================================
@import "survey-system";
```

### Step 3: Import into `theme-dark.scss`

At the **end** of your `theme-dark.scss` file, add:

```scss
// ==============================================================================
// INTERACTIVE WORKFLOW SURVEY SYSTEM - DARK MODE
// ==============================================================================
@import "survey-system-dark";
```

### Step 4: Update Your `_quarto.yml`

Make sure your Quarto configuration points to your theme files:

```yaml
format:
  html:
    theme:
      light: theme.scss
      dark: theme-dark.scss
```

### Step 5: Use the Clean QMD File

Replace your `workflow-survey-system.qmd` with `workflow-survey-system-clean.qmd`. This version has all the CSS removed and relies on your SCSS files.

---

## Required SCSS Variables

The survey system styles use these Bootstrap/Quarto SCSS variables. Make sure they're defined in your theme:

### Colors
- `$primary` - Primary button color
- `$success` - Success/download button color
- `$danger` - Danger/delete button color
- `$warning` - Warning message color
- `$info` - Info message color
- `$white` - White color
- `$body-bg` - Background color for light theme
- `$body-bg-dark` - Background color for dark theme
- `$body-color` - Text color
- `$text-muted` - Muted text color
- `$border-color` - Border color
- `$input-bg` - Input background color

### Grays (for dark theme)
- `$gray-100` - Lightest gray
- `$gray-200`
- `$gray-400`
- `$gray-700`
- `$gray-800`
- `$gray-900` - Darkest gray

If any of these are missing, you can define them at the top of your `theme.scss`:

```scss
// Example defaults (adjust to match your design)
$primary: #007bff;
$success: #28a745;
$danger: #dc3545;
$warning: #ffc107;
$info: #17a2b8;
$white: #ffffff;
$body-bg: #ffffff;
$body-color: #212529;
$text-muted: #6c757d;
$border-color: #dee2e6;
$input-bg: #ffffff;

// Grays
$gray-100: #f8f9fa;
$gray-200: #e9ecef;
$gray-400: #ced4da;
$gray-700: #495057;
$gray-800: #343a40;
$gray-900: #212529;

// Dark theme
$body-bg-dark: #1a1a1a;
```

---

## Alternative: Direct Copy-Paste Method

If you prefer not to use `@import`, you can copy the contents of the SCSS files directly:

### For `theme.scss`

Open `_survey-system.scss`, copy all the code, and paste it at the end of your `theme.scss` file.

### For `theme-dark.scss`

Open `_survey-system-dark.scss`, copy all the code, and paste it at the end of your `theme-dark.scss` file.

---

## Customization

### Change Colors

Edit the variables in your theme files, and the survey system will automatically use them:

```scss
// In theme.scss
$primary: #0066cc;  // Survey buttons will use this color
$success: #00aa00;  // Download button will use this color
```

### Adjust Sidebar Width

In `_survey-system.scss`, find:

```scss
.survey-sidebar {
  width: 450px;
  right: -500px;  // Should be slightly larger than width
  // ...
}
```

### Change Diagram Height

In `_survey-system.scss`, find:

```scss
.svg-viewer-container {
  height: 700px;  // Change this
  // ...
}
```

### Add Custom Styles

You can extend the survey system styles in your main theme files:

```scss
// In theme.scss, after @import "survey-system";

// Custom: Make survey panel wider
.survey-sidebar {
  width: 600px;
  right: -600px;
}

// Custom: Change form label color
.form-group label {
  color: $primary;
}
```

---

## Verification

After integration, verify that:

1. **Render your Quarto document:**
   ```bash
   quarto render workflow-survey-system-clean.qmd
   ```

2. **Check the output:**
   - Survey panel should slide in from the right
   - Buttons should have your theme colors
   - Dark mode should work if you have it enabled

3. **Test in browser:**
   - Click a shape → panel opens
   - Form fields should be styled
   - Buttons should have hover effects

---

## Troubleshooting

### Styles Not Applying

**Check that:**
1. SCSS files are in the correct directory
2. `@import` statements are at the end of your theme files
3. Quarto has been re-rendered after changes
4. Browser cache is cleared (hard refresh: `Ctrl+Shift+R`)

### Variables Not Defined

If you see errors like `Undefined variable $primary`:

1. Add the missing variable definitions to your `theme.scss`
2. Or replace the variable with a hard-coded color in the SCSS partial

### Dark Mode Not Working

**Check that:**
1. `_survey-system-dark.scss` is imported into `theme-dark.scss`
2. Your theme uses `[data-bs-theme="dark"]` selector
3. Dark theme is enabled in Quarto config

---

## Benefits of This Approach

✅ **Cleaner QMD files** - No CSS clutter  
✅ **Centralized styling** - All styles in theme files  
✅ **Theme consistency** - Uses your existing color variables  
✅ **Easy maintenance** - Update styles in one place  
✅ **Dark mode support** - Automatically works with your dark theme  
✅ **Reusable** - Multiple pages can use the same styles  

---

## File Organization

After integration, your project structure should look like:

```
your-project/
├── theme.scss                           # Your light theme
├── theme-dark.scss                      # Your dark theme
├── _survey-system.scss                  # Survey styles
├── _survey-system-dark.scss             # Survey dark styles
├── content/
│   └── workflow-survey-system-clean.qmd # Clean QMD (no CSS)
├── output/
│   └── your_diagram.svg                 # Your SVG diagram
└── _quarto.yml                          # Quarto config
```

---

## Example: Minimal Integration

If you don't have extensive theme files yet, here's a minimal `theme.scss`:

```scss
/*-- scss:defaults --*/
// Basic colors
$primary: #007bff;
$success: #28a745;
$danger: #dc3545;
$warning: #ffc107;
$info: #17a2b8;

/*-- scss:rules --*/
// Import survey system
@import "survey-system";
```

And a minimal `theme-dark.scss`:

```scss
/*-- scss:defaults --*/
$body-bg-dark: #1a1a1a;

/*-- scss:rules --*/
// Import dark theme overrides
@import "survey-system-dark";
```

---

## Need Help?

- See `SETUP_GUIDE.md` for general setup
- See `QUICK_REFERENCE.md` for adding survey links
- Check Quarto documentation: https://quarto.org/docs/output-formats/html-themes.html
