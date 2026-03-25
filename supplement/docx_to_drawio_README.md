# Word Document to Draw.io Flowchart Generator

R function to automatically convert Word document headings into multi-page Draw.io flowcharts.

## Features

- ✅ Converts .docx headings to Draw.io flowchart diagrams
- ✅ **Sequential H1 spine**: H1 headings connected in order
- ✅ **H2 branches**: H2s branch perpendicular from their parent H1
- ✅ **Smart layout**: TB direction = H1 vertical, H2 horizontal right; LR direction = H1 horizontal, H2 vertical down
- ✅ Color-coded rounded rectangles by heading hierarchy
- ✅ Multi-page support: Each H2 gets its own sub-page
- ✅ **Link buttons**: H2s on overview are clickable links (marked with 🔗) to sub-pages
- ✅ Configurable flow direction (top-to-bottom or left-to-right)
- ✅ Exclude specific heading levels
- ✅ Automatic "Back to Overview" links on sub-pages
- ✅ Tidyverse-compatible syntax with `%>%` pipes

## Requirements

```r
install.packages(c("officer", "xml2", "dplyr", "purrr"))
```

## Quick Start

```r
# Source the function
source("docx_to_drawio.R")

# Create flowchart from your Word document
create_flowchart(
  input_file = "my_document.docx",
  output_folder = "output",
  direction = "TB",
  h2_new_page = TRUE
)
```

## Function Parameters

### `create_flowchart()`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_file` | character | *required* | Path to .docx file |
| `output_folder` | character | *required* | Folder where .drawio file will be saved |
| `exclude_levels` | numeric vector | `NULL` | Heading levels to exclude (e.g., `c(3, 4)`) |
| `direction` | character | `"TB"` | Flow direction: `"TB"` (top-bottom) or `"LR"` (left-right) |
| `h2_new_page` | logical | `TRUE` | If `TRUE`, each H2 creates a new diagram page |
| `output_filename` | character | `NULL` | Custom filename without extension (auto-generated if `NULL`) |

## Color Scheme

The function uses a default color palette for heading hierarchy:

- **H1**: Blue (#4A90E2)
- **H2**: Medium Purple (#7B68EE)
- **H3**: Emerald (#50C878)
- **H4**: Sandy Brown (#F4A460)
- **H5**: Light Coral (#E57373)
- **H6**: Gold (#FFD700)

## Layout Structure

### Top-to-Bottom (TB) Direction:
```
H1-1 → H2a → H2b
 ↓
H1-2
 ↓
H1-3 → H2c → H2d → H2e
```
- **H1 spine**: Vertical (top-to-bottom)
- **H2 branches**: Horizontal to the right
- **Connections**: H1s connected sequentially; H2s under same H1 connected horizontally

### Left-to-Right (LR) Direction:
```
H1-1 → H1-2 → H1-3
 ↓              ↓
H2a            H2c
 ↓              ↓
H2b            H2d
               ↓
              H2e
```
- **H1 spine**: Horizontal (left-to-right)
- **H2 branches**: Vertical downward
- **Connections**: H1s connected sequentially; H2s under same H1 connected vertically

## Multi-Page Structure

When `h2_new_page = TRUE`:

**Overview Page:**
- Contains all H1 and H2 headings
- H1 boxes show the main document structure (sequential spine)
- H2 boxes are **clickable link buttons** (marked with 🔗 icon and dashed borders)
- Clicking an H2 navigates to its dedicated sub-page

**Sub-Pages (one per H2):**
- Contains the H2 heading + all its children (H3, H4, etc.)
- H2 box appears here as an **editable node** (this is the "real" version)
- Shows hierarchical tree structure of that section
- Includes "Back to Overview" button to return to main page

**Note**: H2 boxes appear on overview as navigation links only. Edit the actual H2 content on its sub-page.

## Usage Examples

### Example 1: Basic Usage

```r
library(officer)
source("docx_to_drawio.R")

# Convert document with default settings
create_flowchart(
  input_file = "my_document.docx",
  output_folder = "flowcharts"
)
```

### Example 2: Left-to-Right Flow

```r
# Create horizontal flowchart
create_flowchart(
  input_file = "my_document.docx",
  output_folder = "flowcharts",
  direction = "LR"
)
```

### Example 3: Exclude Heading Levels

```r
# Exclude H3 and H4 headings from diagram
create_flowchart(
  input_file = "my_document.docx",
  output_folder = "flowcharts",
  exclude_levels = c(3, 4)
)
```

### Example 4: Single Page Mode

```r
# Put all headings on one page (no H2 sub-pages)
create_flowchart(
  input_file = "my_document.docx",
  output_folder = "flowcharts",
  h2_new_page = FALSE
)
```

### Example 5: Custom Output Name

```r
# Specify custom output filename
create_flowchart(
  input_file = "my_document.docx",
  output_folder = "flowcharts",
  output_filename = "project_workflow_v2"
)
```

### Example 6: Tidyverse Pipeline

```r
library(dplyr)

# Use in a pipeline
"my_document.docx" %>%
  create_flowchart(
    output_folder = "flowcharts",
    exclude_levels = 4,
    direction = "TB"
  )
```

### Example 7: Batch Processing

```r
# Process multiple documents
library(purrr)

docx_files <- list.files("documents", pattern = "\\.docx$", full.names = TRUE)

docx_files %>%
  walk(~create_flowchart(
    input_file = .x,
    output_folder = "flowcharts",
    direction = "TB"
  ))
```

## Document Structure Requirements

Your Word document should use built-in heading styles:

```
Heading 1 (H1)
├── Heading 2 (H2)
│   ├── Heading 3 (H3)
│   └── Heading 3 (H3)
├── Heading 2 (H2)
│   ├── Heading 3 (H3)
│   └── Heading 3 (H3)
└── Heading 2 (H2)

Heading 1 (H1)
└── Heading 2 (H2)
    └── Heading 3 (H3)
```

**Important**: Use Word's built-in heading styles (Heading 1, Heading 2, etc.), not manually formatted text.

## Output

The function creates a `.drawio` XML file that can be:

1. **Opened in Draw.io**:
   - Go to https://app.diagrams.net
   - File → Open → Select your `.drawio` file
   
2. **Imported into other tools**: Compatible with diagrams.net integrations

3. **Edited**: Full Draw.io functionality available for customization

## File Structure

```
your-project/
├── docx_to_drawio.R         # Main function file
├── example_usage.R           # Example scripts
├── your_document.docx        # Input Word document
└── output/                   # Output folder
    └── your_document_flowchart.drawio
```

## Troubleshooting

### No headings found

**Problem**: "No headings found in document" error

**Solution**: Ensure your document uses Word's built-in Heading styles (not just bold text)

### Headings not showing

**Problem**: Some headings don't appear in flowchart

**Solution**: Check if they're excluded via `exclude_levels` parameter

### Layout issues

**Problem**: Boxes overlap or spacing looks off

**Solution**: Try changing `direction` parameter or use single-page mode

### File not saved

**Problem**: Output file not created

**Solution**: Ensure `output_folder` path exists or can be created

## Advanced Customization

To modify colors, spacing, or node sizes, edit these internal variables in `docx_to_drawio.R`:

```r
# In get_heading_color() function - change colors
colors <- c(
  "1" = "#4A90E2",  # Your custom H1 color
  "2" = "#7B68EE",  # Your custom H2 color
  # ...
)

# In calculate_layout() function - change spacing
node_width <- 180      # Box width
node_height <- 60      # Box height
h_spacing <- 80        # Horizontal spacing
v_spacing <- 100       # Vertical spacing
```

## Notes

- The function preserves heading hierarchy from your Word document
- Empty headings are included but may appear as empty boxes
- Very large documents may create complex diagrams - consider excluding lower heading levels
- Draw.io page links work when opened in draw.io/diagrams.net

## License

Free to use and modify for your projects.

## Support

For issues or questions, refer to the example scripts in `example_usage.R`.
