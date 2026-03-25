library(officer)
library(dplyr)

# Source the main function
source("docx_to_drawio.R")

# ============================================================================
# EXAMPLE 1: Create a sample Word document with headings
# ============================================================================

create_sample_document <- function(output_path = "sample_document.docx") {
  
  doc <- read_docx()
  
  # Add content with various heading levels
  doc <- doc %>%
    body_add_par("Project Overview", style = "heading 1") %>%
    body_add_par("This is a sample document to demonstrate flowchart generation.") %>%
    
    body_add_par("Planning Phase", style = "heading 2") %>%
    body_add_par("Initial planning activities...") %>%
    
    body_add_par("Requirements Gathering", style = "heading 3") %>%
    body_add_par("Collect stakeholder requirements...") %>%
    
    body_add_par("Risk Assessment", style = "heading 3") %>%
    body_add_par("Identify and evaluate risks...") %>%
    
    body_add_par("Design Phase", style = "heading 2") %>%
    body_add_par("Design activities...") %>%
    
    body_add_par("Architecture Design", style = "heading 3") %>%
    body_add_par("Define system architecture...") %>%
    
    body_add_par("Database Design", style = "heading 3") %>%
    body_add_par("Design database schema...") %>%
    
    body_add_par("UI/UX Design", style = "heading 3") %>%
    body_add_par("Create user interface mockups...") %>%
    
    body_add_par("Implementation", style = "heading 1") %>%
    body_add_par("Development work...") %>%
    
    body_add_par("Backend Development", style = "heading 2") %>%
    body_add_par("Build server-side components...") %>%
    
    body_add_par("API Development", style = "heading 3") %>%
    body_add_par("Create RESTful APIs...") %>%
    
    body_add_par("Database Implementation", style = "heading 3") %>%
    body_add_par("Set up database...") %>%
    
    body_add_par("Frontend Development", style = "heading 2") %>%
    body_add_par("Build user interface...") %>%
    
    body_add_par("Component Development", style = "heading 3") %>%
    body_add_par("Create reusable components...") %>%
    
    body_add_par("State Management", style = "heading 3") %>%
    body_add_par("Implement state management...") %>%
    
    body_add_par("Testing", style = "heading 1") %>%
    body_add_par("Quality assurance activities...") %>%
    
    body_add_par("Unit Testing", style = "heading 2") %>%
    body_add_par("Test individual components...") %>%
    
    body_add_par("Integration Testing", style = "heading 2") %>%
    body_add_par("Test system integration...") %>%
    
    body_add_par("Deployment", style = "heading 1") %>%
    body_add_par("Release to production...") %>%
    
    body_add_par("Production Setup", style = "heading 2") %>%
    body_add_par("Configure production environment...") %>%
    
    body_add_par("Monitoring Setup", style = "heading 2") %>%
    body_add_par("Set up monitoring and alerts...")
  
  print(doc, target = output_path)
  message("Sample document created: ", output_path)
  return(output_path)
}


# ============================================================================
# EXAMPLE 2: Basic usage - all headings, top-to-bottom
# ============================================================================

example_basic <- function() {
  message("\n=== Example 1: Basic Usage ===\n")
  
  # Create sample document
  sample_doc <- create_sample_document("sample_document.docx")
  
  # Create flowchart
  create_flowchart(
    input_file = sample_doc,
    output_folder = "output",
    direction = "TB",
    h2_new_page = TRUE
  )
}


# ============================================================================
# EXAMPLE 3: Left-to-right flow, exclude H3 headings
# ============================================================================

example_lr_exclude <- function() {
  message("\n=== Example 2: Left-Right Flow, Exclude H3 ===\n")
  
  sample_doc <- "sample_document.docx"
  
  if (!file.exists(sample_doc)) {
    sample_doc <- create_sample_document(sample_doc)
  }
  
  create_flowchart(
    input_file = sample_doc,
    output_folder = "output",
    exclude_levels = 3,  # Exclude H3 headings
    direction = "LR",     # Left to right
    h2_new_page = TRUE
  )
}


# ============================================================================
# EXAMPLE 4: Single page mode (no H2 sub-pages)
# ============================================================================

example_single_page <- function() {
  message("\n=== Example 3: Single Page Mode ===\n")
  
  sample_doc <- "sample_document.docx"
  
  if (!file.exists(sample_doc)) {
    sample_doc <- create_sample_document(sample_doc)
  }
  
  create_flowchart(
    input_file = sample_doc,
    output_folder = "output",
    direction = "TB",
    h2_new_page = FALSE,  # All on one page
    output_filename = "single_page_flowchart"
  )
}


# ============================================================================
# EXAMPLE 5: Custom filename and exclude multiple levels
# ============================================================================

example_custom <- function() {
  message("\n=== Example 5: Custom Settings ===\n")
  
  sample_doc <- "sample_document.docx"
  
  if (!file.exists(sample_doc)) {
    sample_doc <- create_sample_document(sample_doc)
  }
  
  create_flowchart(
    input_file = sample_doc,
    output_folder = "output",
    exclude_levels = c(3, 4),  # Exclude H3 and H4
    direction = "TB",
    h2_new_page = TRUE,
    output_filename = "my_custom_flowchart"
  )
}


# ============================================================================
# EXAMPLE 6: Using with your own document
# ============================================================================

example_your_document <- function(your_docx_path) {
  message("\n=== Using Your Own Document ===\n")
  
  create_flowchart(
    input_file = your_docx_path,
    output_folder = "output",
    exclude_levels = NULL,  # Include all heading levels
    direction = "TB",
    h2_new_page = TRUE
  )
}


# ============================================================================
# Run examples
# ============================================================================

# Run the basic example
example_basic()

# Uncomment to run other examples:
# example_lr_exclude()
# example_single_page()
# example_custom()

# To use with your own document:
# example_your_document("path/to/your/document.docx")
