# ==============================================================================
# HELPER FUNCTION: Add Survey Links to Existing SVG Diagrams
# ==============================================================================
# This function automatically adds survey links to all shapes in your SVG diagram
# 
# Usage:
#   source("add_survey_links.R")
#   add_survey_links_to_svg("output/OSworkflow.svg", "output/OSworkflow_with_surveys.svg")
#

library(xml2)
library(tidyverse)

add_survey_links_to_svg <- function(input_svg_path, output_svg_path = NULL) {
  
  # If no output path specified, overwrite the input
  if (is.null(output_svg_path)) {
    output_svg_path <- input_svg_path
  }
  
  # Check if file exists
  if (!file.exists(input_svg_path)) {
    stop("Input SVG file not found: ", input_svg_path)
  }
  
  cat("Reading SVG file...\n")
  svg_doc <- read_xml(input_svg_path)
  
  # Find all groups (g elements) that likely represent shapes
  # In draw.io SVGs, each shape is typically a <g> element
  groups <- xml_find_all(svg_doc, ".//g[@id]")
  
  cat("Found", length(groups), "groups in the SVG\n")
  
  # Counter for shapes processed
  shapes_processed <- 0
  
  # Process each group
  for (group in groups) {
    group_id <- xml_attr(group, "id")
    
    # Skip if this group already has a link as a child
    existing_link <- xml_find_first(group, "./a")
    if (!inherits(existing_link, "xml_missing")) {
      cat("  Skipping", group_id, "- already has a link\n")
      next
    }
    
    # Try to extract text content from the shape for a better label
    text_elements <- xml_find_all(group, ".//text")
    shape_text <- ""
    
    if (length(text_elements) > 0) {
      # Concatenate all text in this shape
      shape_text <- text_elements %>%
        map_chr(xml_text) %>%
        paste(collapse = " ") %>%
        str_trim()
    }
    
    # If no text, use the group ID
    if (shape_text == "" || is.na(shape_text)) {
      shape_text <- group_id
    }
    
    # Create the survey link URL
    # Format: #survey:SHAPE_ID|SHAPE_TEXT
    survey_url <- paste0("#survey:", group_id, "|", shape_text)
    
    # Get all children of this group
    children <- xml_children(group)
    
    # Create a new <a> element
    link_element <- xml_new_root("a", "xmlns" = "http://www.w3.org/2000/svg")
    xml_set_attr(link_element, "href", survey_url)
    
    # Move all children under the <a> element
    for (child in children) {
      xml_add_child(link_element, xml_clone(child))
      xml_remove(child)
    }
    
    # Add the <a> element to the group
    xml_add_child(group, link_element)
    
    shapes_processed <- shapes_processed + 1
  }
  
  cat("\nProcessed", shapes_processed, "shapes\n")
  cat("Writing modified SVG to:", output_svg_path, "\n")
  
  # Write the modified SVG
  write_xml(svg_doc, output_svg_path)
  
  cat("✅ Done! Your SVG now has survey links.\n")
  cat("\nNext steps:\n")
  cat("1. Open", output_svg_path, "in your browser to verify links work\n")
  cat("2. Use this SVG file in your Quarto document\n")
  cat("3. Click on any shape to test the survey panel\n")
  
  return(invisible(output_svg_path))
}

# ==============================================================================
# ALTERNATIVE: Add Survey Links to .drawio File (More Complex)
# ==============================================================================
# Note: .drawio files are XML-based, but the structure is different from SVG
# For simplicity, we recommend:
# 1. Export your .drawio to SVG with links enabled
# 2. Use the function above to add survey links
# 3. Or manually add links in diagrams.net (easier for small diagrams)

# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================
if (FALSE) {
  # Example 1: Create a new file with survey links
  add_survey_links_to_svg(
    input_svg_path = "output/OSworkflow.svg",
    output_svg_path = "output/OSworkflow_with_surveys.svg"
  )
  
  # Example 2: Overwrite the original file
  add_survey_links_to_svg("output/OSworkflow.svg")
  
  # Example 3: Batch process multiple SVGs
  svg_files <- list.files("output", pattern = "\\.svg$", full.names = TRUE)
  for (svg_file in svg_files) {
    add_survey_links_to_svg(svg_file)
  }
}

# ==============================================================================
# MANUAL METHOD (for reference)
# ==============================================================================
# If you prefer to add links manually in diagrams.net:
#
# 1. Open your diagram in https://app.diagrams.net/
# 2. Select a shape
# 3. Right-click → Edit Link (or Alt+Shift+L)
# 4. In the link field, enter: #survey:shape_1|My Shape Name
#    - Replace "shape_1" with a unique ID for this shape
#    - Replace "My Shape Name" with descriptive text
# 5. Click Apply
# 6. Repeat for all shapes you want to survey
# 7. Export to SVG with "Links" option checked
#
# Link format: #survey:UNIQUE_ID|DISPLAY_TEXT
# ==============================================================================
