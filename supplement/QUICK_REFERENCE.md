# Quick Reference: Adding Survey Links to Diagrams

## Method 1: Manual Links in diagrams.net

### Step-by-Step

1. **Open diagram** at https://app.diagrams.net/
2. **Select shape** you want to make clickable
3. **Right-click** → Edit Link (or press `Alt + Shift + L`)
4. **Enter link:**
   ```
   #survey:UNIQUE_ID|SHAPE_NAME
   ```
   Example: `#survey:data_collect|Data Collection`
   
5. **Click Apply**
6. **Repeat** for all shapes
7. **Export:** File → Export as → SVG
   - ✅ Check "Include a copy of my diagram"
   - ✅ Check "Links"
8. **Save** to `output/your_diagram.svg`

### Link Format Rules

```
#survey:SHAPE_ID|SHAPE_TEXT
         ↑            ↑
    unique ID    display name
```

- **SHAPE_ID**: Unique identifier (no spaces, use underscores)
- **SHAPE_TEXT**: Display name (can have spaces)
- **Separator**: Use `|` (pipe) between ID and text

### Examples

| Shape Type | Good Link | Bad Link |
|------------|-----------|----------|
| Data Collection | `#survey:data_collection\|Data Collection` | `#survey:data collection` ❌ |
| QA Review | `#survey:qa_review\|QA Review` | `#survey:QA Review` ❌ |
| Step 1 | `#survey:step_1\|Step 1: Planning` | `#survey:step 1` ❌ |

---

## Method 2: Automatic with R Function

### For Existing SVG Files

```r
# 1. Load the function
source("add_survey_links.R")

# 2. Run on your SVG
add_survey_links_to_svg("output/your_diagram.svg")

# 3. Done! Links are now added to all shapes
```

### What It Does

- Finds all shapes in your SVG
- Extracts text from each shape
- Creates survey link for each shape
- Preserves all existing styling

### When to Use

✅ Use automatic method when:
- You have >20 shapes
- You want consistent IDs
- You're updating an existing diagram

✅ Use manual method when:
- You have <20 shapes
- You want custom, descriptive IDs
- You only want surveys on specific shapes

---

## Testing Your Links

### In diagrams.net (Before Export)

1. Click **File → Preview** (or `Ctrl + Shift + E`)
2. Click on shapes
3. Should do nothing (links work after export)

### In Browser (After Export)

1. Open the rendered Quarto page
2. Click on a shape
3. Survey panel should slide out
4. Shape name should appear at the top

### Debugging

If links don't work:

1. **Check SVG export settings**
   - "Links" option must be checked
   
2. **Check link format**
   - Must start with `#survey:`
   - Must have `|` separator
   - No spaces in SHAPE_ID

3. **Check browser console** (F12)
   - Look for JavaScript errors
   - Check if click is being captured

---

## Workflow Diagram Link Template

Copy this template for consistent naming:

```
Process Steps:
#survey:step_1|Step 1: [NAME]
#survey:step_2|Step 2: [NAME]
#survey:step_3|Step 3: [NAME]

Decisions:
#survey:decision_1|Decision: [QUESTION]
#survey:decision_2|Decision: [QUESTION]

Outputs:
#survey:output_1|Output: [NAME]
#survey:output_2|Output: [NAME]

Reviews:
#survey:review_1|Review: [NAME]
#survey:review_2|Review: [NAME]
```

---

## Common Patterns

### Sequential Steps
```
#survey:step_01|Step 1: Data Collection
#survey:step_02|Step 2: Data Cleaning
#survey:step_03|Step 3: Analysis
#survey:step_04|Step 4: Reporting
```

### Department/Team
```
#survey:team_data|Data Team Activities
#survey:team_analysis|Analysis Team Activities
#survey:team_qa|QA Team Activities
```

### Status Tracking
```
#survey:planning|Planning Phase
#survey:development|Development Phase
#survey:testing|Testing Phase
#survey:deployment|Deployment Phase
```

---

## Pro Tips

### Tip 1: Use Prefixes
Keep shapes organized with prefixes:
- `step_` for process steps
- `decision_` for decision points
- `doc_` for documentation
- `review_` for review gates

### Tip 2: Number for Order
Use zero-padded numbers for sorting:
```
step_01, step_02, ..., step_09, step_10
```
Not: `step_1, step_2, ..., step_9, step_10`

### Tip 3: Descriptive IDs
Make IDs meaningful:
```
✅ #survey:data_quality_check|Data Quality Check
❌ #survey:shape1|Data Quality Check
```

### Tip 4: Consistent Naming
Pick a convention and stick to it:
```
snake_case: data_collection
kebab-case: data-collection
camelCase: dataCollection
```

---

## Batch Operations

### Adding Same Prefix to Multiple Shapes

In diagrams.net:
1. Select first shape
2. Add link: `#survey:analysis_step1|Analysis Step 1`
3. Copy shape (`Ctrl + C`)
4. Select next shape
5. Paste style (`Ctrl + Shift + V`)
6. Edit link to change ID

### Global Find/Replace After Export

If you need to change many IDs:
1. Export SVG
2. Open in text editor
3. Find: `#survey:old_prefix`
4. Replace: `#survey:new_prefix`
5. Save

---

## Cheat Sheet

| Task | diagrams.net Shortcut |
|------|----------------------|
| Edit Link | `Alt + Shift + L` |
| Edit Tooltip | `Alt + Shift + T` |
| Preview | `Ctrl + Shift + E` |
| Copy Style | `Ctrl + Shift + C` |
| Paste Style | `Ctrl + Shift + V` |

| Task | After Export |
|------|-------------|
| Test Links | Click shapes in browser |
| View Source | Right-click → Inspect |
| Check Links | Search for `#survey:` in SVG |

---

## Troubleshooting Checklist

- [ ] SVG exported with "Links" option checked
- [ ] Link format is `#survey:ID|TEXT`
- [ ] No spaces in SHAPE_ID portion
- [ ] IDs are unique (no duplicates)
- [ ] SVG file is in correct folder
- [ ] Quarto document points to correct SVG
- [ ] Page has been re-rendered after changes
- [ ] JavaScript console shows no errors

---

## Example: Complete Workflow

Let's say you have a 5-step workflow:

### 1. Open diagrams.net
```
https://app.diagrams.net/
```

### 2. Add Links to Each Step
```
Step 1: #survey:collect_data|Collect Data
Step 2: #survey:clean_data|Clean Data  
Step 3: #survey:analyze_data|Analyze Data
Step 4: #survey:create_report|Create Report
Step 5: #survey:review_publish|Review & Publish
```

### 3. Export SVG
- File → Export as → SVG
- ✅ Links
- ✅ Include a copy of my diagram
- Save to `output/workflow.svg`

### 4. Update QMD
```r
DIAGRAM_FILE <- "workflow.svg"
```

### 5. Render
Click Render in RStudio

### 6. Test
Click each step → Survey should open

---

## Need Help?

See `SETUP_GUIDE.md` for comprehensive documentation!
