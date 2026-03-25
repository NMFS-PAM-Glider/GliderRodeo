library(officer)
library(xml2)
library(dplyr)
library(purrr)

#' Create Draw.io Flowchart from Word Document Headings
#'
#' @param input_file Path to .docx file
#' @param output_folder Folder path where .drawio file will be saved
#' @param exclude_levels Numeric vector of heading levels to exclude (e.g., c(4, 5))
#' @param direction Flow direction: "TB" (top-bottom) or "LR" (left-right)
#' @param h2_new_page Logical. If TRUE, each H2 creates a new diagram page
#' @param output_filename Optional custom filename (without extension)
#'
#' @return Path to created .drawio file
#' @export
create_flowchart <- function(input_file,
                              output_folder,
                              exclude_levels = NULL,
                              direction = "TB",
                              h2_new_page = TRUE,
                              output_filename = NULL) {
  
  # Validate inputs
  if (!file.exists(input_file)) {
    stop("Input file does not exist: ", input_file)
  }
  
  if (!dir.exists(output_folder)) {
    dir.create(output_folder, recursive = TRUE)
    message("Created output folder: ", output_folder)
  }
  
  if (!direction %in% c("TB", "LR")) {
    stop("direction must be 'TB' (top-bottom) or 'LR' (left-right)")
  }
  
  # Read docx file
  message("Reading document...")
  doc <- read_docx(input_file)
  
  # Extract headings
  headings_df <- extract_headings(doc, exclude_levels)
  
  if (nrow(headings_df) == 0) {
    stop("No headings found in document")
  }
  
  message("Found ", nrow(headings_df), " headings")
  
  # Create draw.io XML structure
  message("Generating flowchart...")
  drawio_xml <- create_drawio_xml(headings_df, direction, h2_new_page)
  
  # Save file
  if (is.null(output_filename)) {
    base_name <- tools::file_path_sans_ext(basename(input_file))
    output_filename <- paste0(base_name, "_flowchart")
  }
  
  output_path <- file.path(output_folder, paste0(output_filename, ".drawio"))
  write_xml(drawio_xml, output_path)
  
  message("Flowchart saved to: ", output_path)
  return(invisible(output_path))
}


#' Extract headings from Word document
#' @keywords internal
extract_headings <- function(doc, exclude_levels = NULL) {
  
  # Get document content
  content <- docx_summary(doc)
  
  # Filter for headings
  headings <- content %>%
    filter(content_type == "paragraph",
           grepl("^heading", style_name, ignore.case = TRUE)) %>%
    mutate(
      # Extract heading level from style name
      level = as.numeric(gsub(".*?(\\d+).*", "\\1", style_name))
    ) %>%
    # Remove any rows with NA level or text
    filter(!is.na(level), !is.na(text), text != "") %>%
    select(level, text)
  
  # Remove excluded levels
  if (!is.null(exclude_levels)) {
    headings <- headings %>%
      filter(!level %in% exclude_levels)
  }
  
  # Return empty if no headings
  if (nrow(headings) == 0) {
    return(headings %>%
             mutate(id = integer(),
                    parent_id = integer(),
                    h1_parent = integer(),
                    h2_parent = integer()))
  }
  
  # Add hierarchy tracking
  headings <- headings %>%
    mutate(
      id = row_number(),
      parent_id = NA_integer_,
      h1_parent = NA_integer_,
      h2_parent = NA_integer_
    )
  
  # Assign parent relationships
  for (i in 1:nrow(headings)) {
    current_level <- headings$level[i]
    
    # Skip if current_level is NA
    if (is.na(current_level)) next
    
    if (current_level > 1) {
      # Find most recent parent (previous heading with lower level)
      for (j in (i-1):1) {
        if (j < 1) break
        if (!is.na(headings$level[j]) && headings$level[j] < current_level) {
          headings$parent_id[i] <- headings$id[j]
          break
        }
      }
    }
    
    # Track H1 parent
    if (current_level == 1) {
      headings$h1_parent[i] <- headings$id[i]
    } else {
      for (j in (i-1):1) {
        if (j < 1) break
        if (!is.na(headings$level[j]) && headings$level[j] == 1) {
          headings$h1_parent[i] <- headings$id[j]
          break
        }
      }
    }
    
    # Track H2 parent
    if (current_level == 2) {
      headings$h2_parent[i] <- headings$id[i]
    } else if (current_level > 2) {
      for (j in (i-1):1) {
        if (j < 1) break
        if (!is.na(headings$level[j]) && headings$level[j] == 2) {
          headings$h2_parent[i] <- headings$id[j]
          break
        }
      }
    }
  }
  
  return(headings)
}


#' Get color for heading level
#' @keywords internal
get_heading_color <- function(level) {
  colors <- c(
    "1" = "#4A90E2",  # Blue for H1
    "2" = "#7B68EE",  # Medium Purple for H2
    "3" = "#50C878",  # Emerald for H3
    "4" = "#F4A460",  # Sandy Brown for H4
    "5" = "#E57373",  # Light Coral for H5
    "6" = "#FFD700"   # Gold for H6
  )
  
  return(colors[as.character(level)])
}


#' Create Draw.io XML structure
#' @keywords internal
create_drawio_xml <- function(headings_df, direction, h2_new_page) {
  
  # Create root mxfile element
  root <- xml_new_root("mxfile", 
                       host = "app.diagrams.net",
                       modified = format(Sys.time(), "%Y-%m-%dT%H:%M:%S"),
                       agent = "R-drawio-generator",
                       version = "21.1.0")
  
  if (h2_new_page) {
    # Multi-page mode: Main page + one page per H2
    create_multipage_diagram(root, headings_df, direction)
  } else {
    # Single page mode: All headings on one page
    create_singlepage_diagram(root, headings_df, direction)
  }
  
  return(root)
}


#' Create multi-page diagram
#' @keywords internal
create_multipage_diagram <- function(root, headings_df, direction) {
  
  # Page 1: Overview with H1 and H2 headings (H2s as link buttons only)
  main_headings <- headings_df %>%
    filter(level %in% c(1, 2))
  
  diagram_main <- xml_add_child(root, "diagram", 
                                 id = "main-page",
                                 name = "Overview")
  
  add_overview_content(diagram_main, main_headings, direction)
  
  # Create a page for each H2
  h2_headings <- headings_df %>%
    filter(level == 2)
  
  for (i in 1:nrow(h2_headings)) {
    h2_id <- h2_headings$id[i]
    h2_text <- h2_headings$text[i]
    
    # Get all headings under this H2 (including the H2 itself)
    h2_and_children <- headings_df %>%
      filter(id == h2_id | h2_parent == h2_id)
    
    if (nrow(h2_and_children) > 0) {
      # Create page
      page_id <- paste0("page-h2-", h2_id)
      diagram_sub <- xml_add_child(root, "diagram",
                                    id = page_id,
                                    name = h2_text)
      
      add_subpage_content(diagram_sub, h2_and_children, direction, 
                         parent_text = h2_text,
                         page_id = page_id)
    }
  }
}


#' Create single-page diagram
#' @keywords internal
create_singlepage_diagram <- function(root, headings_df, direction) {
  diagram <- xml_add_child(root, "diagram",
                           id = "main-page",
                           name = "Flowchart")
  
  # Use subpage layout function (hierarchical tree) for single page
  add_subpage_content(diagram, headings_df, direction, 
                     parent_text = NULL,
                     page_id = "main-page")
}


#' Add overview page content (H1 and H2 as link buttons)
#' @keywords internal
add_overview_content <- function(diagram, headings_df, direction) {
  
  mxGraphModel <- xml_add_child(diagram, "mxGraphModel",
                                dx = "1122",
                                dy = "671",
                                grid = "1",
                                gridSize = "10",
                                guides = "1",
                                tooltips = "1",
                                connect = "1",
                                arrows = "1",
                                fold = "1",
                                page = "1",
                                pageScale = "1",
                                pageWidth = "850",
                                pageHeight = "1100",
                                math = "0",
                                shadow = "0")
  
  root_elem <- xml_add_child(mxGraphModel, "root")
  xml_add_child(root_elem, "mxCell", id = "0")
  xml_add_child(root_elem, "mxCell", id = "1", parent = "0")
  
  # Calculate layout for overview
  layout <- calculate_overview_layout(headings_df, direction)
  
  # Add H1 nodes
  h1_nodes <- layout$nodes %>% filter(level == 1)
  for (i in 1:nrow(h1_nodes)) {
    node <- h1_nodes[i, ]
    
    style <- sprintf(
      "rounded=1;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=#000000;fontColor=#FFFFFF;fontSize=14;",
      get_heading_color(node$level)
    )
    
    cell_id <- paste0("node-", node$id)
    
    xml_add_child(root_elem, "mxCell",
                  id = cell_id,
                  value = node$text,
                  style = style,
                  vertex = "1",
                  parent = "1") %>%
      xml_add_child("mxGeometry",
                    x = as.character(node$x),
                    y = as.character(node$y),
                    width = as.character(node$width),
                    height = as.character(node$height),
                    as = "geometry")
  }
  
  # Add H2 nodes as link buttons
  h2_nodes <- layout$nodes %>% filter(level == 2)
  for (i in 1:nrow(h2_nodes)) {
    node <- h2_nodes[i, ]
    
    # Style for link button - dashed border and link icon
    style <- sprintf(
      "rounded=1;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=#000000;fontColor=#FFFFFF;fontSize=12;dashed=1;dashPattern=3 3;strokeWidth=2;",
      get_heading_color(node$level)
    )
    
    cell_id <- paste0("node-", node$id)
    page_id <- paste0("page-h2-", node$id)
    
    # Add link to navigate to sub-page
    link_value <- sprintf("%s 🔗", node$text)
    link_url <- paste0("data:page/id,", page_id)
    
    # Create UserObject with link instead of mxCell
    user_obj <- xml_add_child(root_elem, "UserObject",
                              label = link_value,
                              link = link_url,
                              id = cell_id)
    
    xml_add_child(user_obj, "mxCell",
                  style = style,
                  vertex = "1",
                  parent = "1") %>%
      xml_add_child("mxGeometry",
                    x = as.character(node$x),
                    y = as.character(node$y),
                    width = as.character(node$width),
                    height = as.character(node$height),
                    as = "geometry")
  }
  
  # Add edges
  for (i in 1:nrow(layout$edges)) {
    edge <- layout$edges[i, ]
    
    edge_id <- paste0("edge-", i)
    source_id <- paste0("node-", edge$from)
    target_id <- paste0("node-", edge$to)
    
    xml_add_child(root_elem, "mxCell",
                  id = edge_id,
                  style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;",
                  edge = "1",
                  parent = "1",
                  source = source_id,
                  target = target_id) %>%
      xml_add_child("mxGeometry",
                    relative = "1",
                    as = "geometry")
  }
}


#' Add subpage content (H2 and its children)
#' @keywords internal
add_subpage_content <- function(diagram, headings_df, direction, parent_text, page_id) {
  
  mxGraphModel <- xml_add_child(diagram, "mxGraphModel",
                                dx = "1122",
                                dy = "671",
                                grid = "1",
                                gridSize = "10",
                                guides = "1",
                                tooltips = "1",
                                connect = "1",
                                arrows = "1",
                                fold = "1",
                                page = "1",
                                pageScale = "1",
                                pageWidth = "850",
                                pageHeight = "1100",
                                math = "0",
                                shadow = "0")
  
  root_elem <- xml_add_child(mxGraphModel, "root")
  xml_add_child(root_elem, "mxCell", id = "0")
  xml_add_child(root_elem, "mxCell", id = "1", parent = "0")
  
  # Calculate layout
  layout <- calculate_subpage_layout(headings_df, direction)
  
  # Add nodes
  for (i in 1:nrow(layout$nodes)) {
    node <- layout$nodes[i, ]
    
    style <- sprintf(
      "rounded=1;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=#000000;fontColor=#FFFFFF;fontSize=14;",
      get_heading_color(node$level)
    )
    
    cell_id <- paste0("node-", node$id)
    
    xml_add_child(root_elem, "mxCell",
                  id = cell_id,
                  value = node$text,
                  style = style,
                  vertex = "1",
                  parent = "1") %>%
      xml_add_child("mxGeometry",
                    x = as.character(node$x),
                    y = as.character(node$y),
                    width = as.character(node$width),
                    height = as.character(node$height),
                    as = "geometry")
  }
  
  # Add edges
  for (i in 1:nrow(layout$edges)) {
    edge <- layout$edges[i, ]
    
    edge_id <- paste0("edge-", i)
    source_id <- paste0("node-", edge$from)
    target_id <- paste0("node-", edge$to)
    
    xml_add_child(root_elem, "mxCell",
                  id = edge_id,
                  style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;",
                  edge = "1",
                  parent = "1",
                  source = source_id,
                  target = target_id) %>%
      xml_add_child("mxGeometry",
                    relative = "1",
                    as = "geometry")
  }
  
  # Add "Back" button
  back_x <- 50
  back_y <- 50
  
  # Create UserObject with link for Back button
  back_obj <- xml_add_child(root_elem, "UserObject",
                            label = "← Back to Overview",
                            link = "data:page/id,main-page",
                            id = "back-button")
  
  xml_add_child(back_obj, "mxCell",
                style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#D3D3D3;strokeColor=#000000;fontColor=#000000;fontSize=12;",
                vertex = "1",
                parent = "1") %>%
    xml_add_child("mxGeometry",
                  x = as.character(back_x),
                  y = as.character(back_y),
                  width = "150",
                  height = "40",
                  as = "geometry")
}


#' Calculate overview page layout (H1 spine with H2 branches)
#' @keywords internal
calculate_overview_layout <- function(headings_df, direction) {
  
  if (nrow(headings_df) == 0) {
    return(list(nodes = data.frame(), edges = data.frame()))
  }
  
  # Settings
  node_width <- 180
  node_height <- 60
  h_spacing <- 100
  v_spacing <- 100
  
  start_x <- 150
  start_y <- 150
  
  # Separate H1 and H2
  h1_headings <- headings_df %>% filter(level == 1)
  h2_headings <- headings_df %>% filter(level == 2)
  
  # Initialize nodes dataframe
  nodes <- headings_df %>%
    mutate(
      x = NA_real_,
      y = NA_real_,
      width = node_width,
      height = node_height
    )
  
  # Initialize edges list
  edges_list <- list()
  
  if (direction == "TB") {
    # Top-to-Bottom: H1 vertical spine, H2 horizontal branches to the right
    
    # Position H1s vertically
    for (i in 1:nrow(h1_headings)) {
      h1_idx <- which(nodes$id == h1_headings$id[i])
      nodes$x[h1_idx] <- start_x
      nodes$y[h1_idx] <- start_y + (i - 1) * (node_height + v_spacing)
      
      # Connect H1s sequentially
      if (i > 1) {
        edges_list[[length(edges_list) + 1]] <- data.frame(
          from = h1_headings$id[i - 1],
          to = h1_headings$id[i]
        )
      }
    }
    
    # Position H2s to the right of their parent H1
    for (i in 1:nrow(h1_headings)) {
      h1_id <- h1_headings$id[i]
      h1_idx <- which(nodes$id == h1_id)
      h1_x <- nodes$x[h1_idx]
      h1_y <- nodes$y[h1_idx]
      
      # Get H2s under this H1
      h2_under_h1 <- h2_headings %>% filter(h1_parent == h1_id)
      
      if (nrow(h2_under_h1) > 0) {
        # Position H2s horizontally to the right
        for (j in 1:nrow(h2_under_h1)) {
          h2_idx <- which(nodes$id == h2_under_h1$id[j])
          nodes$x[h2_idx] <- h1_x + (node_width + h_spacing) * j
          nodes$y[h2_idx] <- h1_y
          
          # Connect H1 to first H2
          if (j == 1) {
            edges_list[[length(edges_list) + 1]] <- data.frame(
              from = h1_id,
              to = h2_under_h1$id[j]
            )
          }
          
          # Connect H2s sequentially
          if (j > 1) {
            edges_list[[length(edges_list) + 1]] <- data.frame(
              from = h2_under_h1$id[j - 1],
              to = h2_under_h1$id[j]
            )
          }
        }
      }
    }
    
  } else {
    # Left-to-Right: H1 horizontal spine, H2 vertical branches downward
    
    # Position H1s horizontally
    for (i in 1:nrow(h1_headings)) {
      h1_idx <- which(nodes$id == h1_headings$id[i])
      nodes$x[h1_idx] <- start_x + (i - 1) * (node_width + h_spacing)
      nodes$y[h1_idx] <- start_y
      
      # Connect H1s sequentially
      if (i > 1) {
        edges_list[[length(edges_list) + 1]] <- data.frame(
          from = h1_headings$id[i - 1],
          to = h1_headings$id[i]
        )
      }
    }
    
    # Position H2s below their parent H1
    for (i in 1:nrow(h1_headings)) {
      h1_id <- h1_headings$id[i]
      h1_idx <- which(nodes$id == h1_id)
      h1_x <- nodes$x[h1_idx]
      h1_y <- nodes$y[h1_idx]
      
      # Get H2s under this H1
      h2_under_h1 <- h2_headings %>% filter(h1_parent == h1_id)
      
      if (nrow(h2_under_h1) > 0) {
        # Position H2s vertically below
        for (j in 1:nrow(h2_under_h1)) {
          h2_idx <- which(nodes$id == h2_under_h1$id[j])
          nodes$x[h2_idx] <- h1_x
          nodes$y[h2_idx] <- h1_y + (node_height + v_spacing) * j
          
          # Connect H1 to first H2
          if (j == 1) {
            edges_list[[length(edges_list) + 1]] <- data.frame(
              from = h1_id,
              to = h2_under_h1$id[j]
            )
          }
          
          # Connect H2s sequentially
          if (j > 1) {
            edges_list[[length(edges_list) + 1]] <- data.frame(
              from = h2_under_h1$id[j - 1],
              to = h2_under_h1$id[j]
            )
          }
        }
      }
    }
  }
  
  # Combine edges
  if (length(edges_list) > 0) {
    edges <- do.call(rbind, edges_list)
  } else {
    edges <- data.frame(from = integer(), to = integer())
  }
  
  return(list(nodes = nodes, edges = edges))
}


#' Calculate subpage layout (H2 and its children in hierarchical tree)
#' @keywords internal
calculate_subpage_layout <- function(headings_df, direction) {
  
  if (nrow(headings_df) == 0) {
    return(list(nodes = data.frame(), edges = data.frame()))
  }
  
  # Settings
  node_width <- 180
  node_height <- 60
  h_spacing <- 80
  v_spacing <- 100
  
  start_x <- 150
  start_y <- 150
  
  # Build hierarchy tree
  nodes <- headings_df %>%
    arrange(id) %>%
    mutate(
      x = NA_real_,
      y = NA_real_,
      width = node_width,
      height = node_height
    )
  
  # Position nodes based on direction (standard hierarchical layout)
  if (direction == "TB") {
    nodes <- position_nodes_tb(nodes, start_x, start_y, node_width, node_height, h_spacing, v_spacing)
  } else {
    nodes <- position_nodes_lr(nodes, start_x, start_y, node_width, node_height, h_spacing, v_spacing)
  }
  
  # Create edges
  edges <- nodes %>%
    filter(!is.na(parent_id)) %>%
    select(from = parent_id, to = id)
  
  return(list(nodes = nodes, edges = edges))
}


#' Position nodes top-to-bottom
#' @keywords internal
position_nodes_tb <- function(nodes, start_x, start_y, node_width, node_height, h_spacing, v_spacing) {
  
  # Group by level
  for (lvl in sort(unique(nodes$level))) {
    level_nodes <- which(nodes$level == lvl)
    
    for (i in seq_along(level_nodes)) {
      idx <- level_nodes[i]
      
      # Y position based on level
      nodes$y[idx] <- start_y + (lvl - 1) * (node_height + v_spacing)
      
      # X position: distribute horizontally
      parent_id <- nodes$parent_id[idx]
      
      if (is.na(parent_id)) {
        # Root nodes: space them out
        root_count <- sum(is.na(nodes$parent_id) & nodes$level == lvl)
        root_index <- sum(is.na(nodes$parent_id[1:idx]) & nodes$level[1:idx] == lvl)
        nodes$x[idx] <- start_x + (root_index - 1) * (node_width + h_spacing)
      } else {
        # Child nodes: position relative to parent
        siblings <- which(nodes$parent_id == parent_id & !is.na(nodes$parent_id))
        sibling_index <- which(siblings == idx)
        n_siblings <- length(siblings)
        
        parent_x <- nodes$x[nodes$id == parent_id]
        
        # Check if parent has been positioned
        if (length(parent_x) == 0 || is.na(parent_x)) {
          # Parent not positioned yet - use default spacing
          nodes$x[idx] <- start_x + (idx - 1) * (node_width + h_spacing)
        } else if (n_siblings == 1) {
          nodes$x[idx] <- parent_x
        } else {
          total_width <- (n_siblings - 1) * (node_width + h_spacing)
          offset <- total_width / 2
          nodes$x[idx] <- parent_x - offset + (sibling_index - 1) * (node_width + h_spacing)
        }
      }
    }
  }
  
  return(nodes)
}


#' Position nodes left-to-right
#' @keywords internal
position_nodes_lr <- function(nodes, start_x, start_y, node_width, node_height, h_spacing, v_spacing) {
  
  # Group by level
  for (lvl in sort(unique(nodes$level))) {
    level_nodes <- which(nodes$level == lvl)
    
    for (i in seq_along(level_nodes)) {
      idx <- level_nodes[i]
      
      # X position based on level
      nodes$x[idx] <- start_x + (lvl - 1) * (node_width + h_spacing)
      
      # Y position: distribute vertically
      parent_id <- nodes$parent_id[idx]
      
      if (is.na(parent_id)) {
        # Root nodes: space them out
        root_count <- sum(is.na(nodes$parent_id) & nodes$level == lvl)
        root_index <- sum(is.na(nodes$parent_id[1:idx]) & nodes$level[1:idx] == lvl)
        nodes$y[idx] <- start_y + (root_index - 1) * (node_height + v_spacing)
      } else {
        # Child nodes: position relative to parent
        siblings <- which(nodes$parent_id == parent_id & !is.na(nodes$parent_id))
        sibling_index <- which(siblings == idx)
        n_siblings <- length(siblings)
        
        parent_y <- nodes$y[nodes$id == parent_id]
        
        # Check if parent has been positioned
        if (length(parent_y) == 0 || is.na(parent_y)) {
          # Parent not positioned yet - use default spacing
          nodes$y[idx] <- start_y + (idx - 1) * (node_height + v_spacing)
        } else if (n_siblings == 1) {
          nodes$y[idx] <- parent_y
        } else {
          total_height <- (n_siblings - 1) * (node_height + v_spacing)
          offset <- total_height / 2
          nodes$y[idx] <- parent_y - offset + (sibling_index - 1) * (node_height + v_spacing)
        }
      }
    }
  }
  
  return(nodes)
}
