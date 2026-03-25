# Interactive Workflow Survey System - Setup Guide

## Overview

This system allows users to click on shapes in a workflow diagram and fill out surveys about each component. All responses are stored locally and can be downloaded as CSV files for version control in GitHub.

## Features

✅ **Interactive Diagram** - Pan, zoom, and click on shapes  
✅ **Sliding Survey Panel** - Clean interface for data entry  
✅ **Password Protected** - Simple shared password for editing  
✅ **Pre-filled Forms** - Editing shows previous responses  
✅ **Complete History** - All submissions are logged with timestamps  
✅ **CSV Export** - Download data for GitHub commits  
✅ **Works Out of the Box** - Minimal configuration needed  

---

## Quick Start for Template Users

### Step 1: Copy the Template

1. Copy these files to your project:
   - `workflow-survey-system.qmd`
   - `add_survey_links.R` (optional, for existing diagrams)

2. Place your SVG diagram in the `output/` folder

### Step 2: Configure Settings

Open `workflow-survey-system.qmd` and edit the R setup chunk:

```r
# ============================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================
SURVEY_PASSWORD <- "workflow2024"  # Change this to your desired password
DIAGRAM_FILE <- "OSworkflow.svg"   # Your SVG diagram filename
```

**Change:**
- `SURVEY_PASSWORD` - Set your own password
- `DIAGRAM_FILE` - Use your SVG filename

### Step 3: Add Survey Links to Your Diagram

You have **two options**:

#### Option A: Manually in diagrams.net (Recommended for <20 shapes)

1. Open your diagram at https://app.diagrams.net/
2. Select a shape
3. Right-click → **Edit Link** (or `Alt+Shift+L`)
4. Enter link format: `#survey:SHAPE_ID|SHAPE_TEXT`
   - Example: `#survey:data_collection|Data Collection`
   - `SHAPE_ID` = Unique identifier (no spaces)
   - `SHAPE_TEXT` = Display name for the shape
5. Click **Apply**
6. Repeat for all shapes
7. **File → Export as → SVG**
   - ✅ Check "Include a copy of my diagram"
   - ✅ Check "Links"
8. Save to `output/your_diagram.svg`

#### Option B: Automatically with R Function (For >20 shapes)

1. Export your diagram from diagrams.net to SVG (without links)
2. Save it to `output/` folder
3. In R Console:

```r
source("add_survey_links.R")
add_survey_links_to_svg("output/your_diagram.svg")
```

This automatically adds survey links to all shapes!

### Step 4: Customize Survey Questions (Optional)

In `workflow-survey-system.qmd`, find the survey form section and edit questions:

```html
<div class="form-group">
  <label for="question1">Question 1: YOUR QUESTION HERE</label>
  <select id="question1" required>
    <option value="">-- Select --</option>
    <option value="Option1">Option 1</option>
    <option value="Option2">Option 2</option>
    <!-- Add more options -->
  </select>
</div>
```

**To add a question:** Copy a `<div class="form-group">` block and:
- Change `question1` to `question6`, `question7`, etc.
- Update the label text
- Update the options

**Don't forget to also update:**
- The JavaScript `saveResponse()` function to include new questions
- The CSV headers in `downloadCSV()` function

### Step 5: Render and Test

1. In RStudio, open `workflow-survey-system.qmd`
2. Click **Render** (or use `quarto preview`)
3. Click on a shape in your diagram
4. Fill out the survey
5. Enter password
6. Submit
7. Download CSV and commit to GitHub

---

## User Workflow

### For Regular Users

1. **View Diagram** - Navigate to the page with your workflow
2. **Click a Shape** - Survey panel slides out from the right
3. **Review Previous Entry** - If you've submitted before, see your last response
4. **Edit/Update** - Form is pre-filled, make changes as needed
5. **Submit** - Enter password and submit
6. **Download Data** - Scroll to bottom, click "Download All Responses (CSV)"
7. **Commit to GitHub** - Save the CSV file and push to your repo

### First-Time Setup

When users first clone your template:

1. They get a working survey system out of the box
2. They only need to:
   - Change the password in the config
   - Add their own diagram
   - Optionally customize questions

---

## File Structure

```
your-project/
├── workflow-survey-system.qmd    # Main Quarto document
├── add_survey_links.R            # Helper function (optional)
├── output/
│   └── your_diagram.svg          # Your workflow diagram
├── _site/                        # Rendered output (auto-generated)
│   └── workflow-survey-system.html
└── data/                         # Store downloaded CSVs here
    └── workflow_responses_YYYY-MM-DD.csv
```

---

## Survey Link Format

Links in your SVG should follow this format:

```
#survey:SHAPE_ID|SHAPE_TEXT
```

**Examples:**

- `#survey:step1|Data Collection`
- `#survey:analysis_phase|Analysis Phase`
- `#survey:qa_review|QA Review`

**Rules:**
- `SHAPE_ID` must be unique for each shape
- No spaces in `SHAPE_ID` (use underscores)
- `SHAPE_TEXT` can have spaces and special characters
- Separate ID and text with `|` (pipe character)

---

## Data Storage

### How It Works

- **LocalStorage**: Responses are saved in your browser's localStorage
- **Per User**: Each person who opens the page on their computer has their own data
- **Persistent**: Data stays even after closing the browser
- **Exportable**: Download as CSV anytime

### CSV Format

```csv
timestamp,username,shape_id,shape_text,question1,question2,question3,question4,question5
2024-02-02T10:30:00.000Z,"Alice","step1","Data Collection","In Progress","High","No Blockers","Adequate","On Track"
2024-02-02T14:15:00.000Z,"Alice","step1","Data Collection","In Progress","Medium","No Blockers","Adequate","On Track"
```

### Version Control Workflow

1. User fills out surveys over time
2. Periodically downloads CSV
3. Saves CSV to `data/` folder in repo
4. Commits and pushes to GitHub
5. Can analyze responses with R scripts

---

## Customization Guide

### Change Number of Questions

1. **Add questions** in the HTML form section
2. **Update JavaScript** in the `saveResponse()` function:

```javascript
const response = {
  timestamp: new Date().toISOString(),
  username: document.getElementById('username').value,
  shape_id: currentShapeId,
  shape_text: currentShapeText,
  question1: document.getElementById('question1').value,
  question2: document.getElementById('question2').value,
  question3: document.getElementById('question3').value,
  question4: document.getElementById('question4').value,
  question5: document.getElementById('question5').value,
  question6: document.getElementById('question6').value  // ADD NEW QUESTIONS
};
```

3. **Update CSV download** in the `downloadCSV()` function:

```javascript
const headers = ['timestamp', 'username', 'shape_id', 'shape_text', 
                 'question1', 'question2', 'question3', 'question4', 
                 'question5', 'question6'];  // ADD NEW HEADERS
```

### Change Question Types

The system currently supports **select dropdowns**. To add other types:

**Text Input:**
```html
<div class="form-group">
  <label for="notes">Additional Notes:</label>
  <input type="text" id="notes" placeholder="Enter notes">
</div>
```

**Text Area:**
```html
<div class="form-group">
  <label for="comments">Comments:</label>
  <textarea id="comments" rows="4"></textarea>
</div>
```

**Radio Buttons:**
```html
<div class="form-group">
  <label>Status:</label>
  <label><input type="radio" name="status" value="yes"> Yes</label>
  <label><input type="radio" name="status" value="no"> No</label>
</div>
```

### Change Password

Edit the R setup chunk:

```r
SURVEY_PASSWORD <- "your_new_password_here"
```

### Change Diagram

Replace the SVG file and update:

```r
DIAGRAM_FILE <- "new_diagram.svg"
```

---

## Troubleshooting

### Survey Panel Doesn't Open

- **Check link format**: Must be `#survey:ID|TEXT`
- **Check SVG export**: "Links" option must be checked
- **Check browser console**: Press F12, look for errors

### Password Not Working

- Check you haven't changed the password in the qmd but not re-rendered
- Password is case-sensitive
- Make sure you're using the same password in config and when submitting

### Previous Entry Not Showing

- This is normal if it's the first time clicking that shape
- Check browser localStorage (F12 → Application → Local Storage)
- Make sure you submitted with the correct password

### CSV Download Not Working

- Check if you have responses (look at count at bottom)
- Try a different browser
- Check browser's download settings

### Data Lost After Closing Browser

- LocalStorage should persist, but:
- Make sure you're using the same browser
- Check if browser is in private/incognito mode (data won't persist)
- **Solution**: Download CSV regularly!

---

## Advanced Features

### Analyzing Responses in R

Once you've downloaded CSVs, you can analyze them:

```r
library(tidyverse)

# Read all response files
responses <- list.files("data", pattern = "workflow_responses.*\\.csv", 
                       full.names = TRUE) %>%
  map_df(read_csv)

# View summary by shape
responses %>%
  group_by(shape_id, shape_text) %>%
  summarize(
    n_responses = n(),
    latest_status = last(question1),
    .groups = "drop"
  )

# Timeline of updates
responses %>%
  mutate(date = as.Date(timestamp)) %>%
  count(date, shape_id) %>%
  ggplot(aes(date, n, color = shape_id)) +
  geom_line() +
  labs(title = "Survey Responses Over Time")
```

### Multiple Diagrams

To have multiple diagrams with surveys:

1. Create separate `.qmd` files for each diagram
2. Each can have its own password and questions
3. Responses are stored separately per page (based on URL)

### Sharing Data Across Team

Since localStorage is per-browser:

1. Team members download their CSVs regularly
2. Commit to a shared GitHub repo
3. Merge CSV files in R for team analysis

---

## FAQ

**Q: Can multiple people edit the same shape?**  
A: Yes! Each person's submissions are logged separately with timestamps and usernames.

**Q: What if I forget the password?**  
A: Change it in the R config chunk and re-render the page.

**Q: Can I delete a response?**  
A: Not directly in the UI, but you can download the CSV, remove the row, and that's your new record.

**Q: Is this secure?**  
A: This is designed for internal team use with a shared password. It's not meant for sensitive data requiring encryption.

**Q: Can I use this without GitHub?**  
A: Yes! The survey system works locally. You just need to manually share CSV files.

**Q: How many responses can it handle?**  
A: LocalStorage typically allows 5-10MB. At ~200 bytes per response, that's 25,000-50,000 responses. More than enough!

---

## Support

For issues or questions:
1. Check this documentation
2. Review the code comments
3. Open an issue on GitHub
4. Contact the template creator

---

## License

This template is open source and free to use for your projects!

