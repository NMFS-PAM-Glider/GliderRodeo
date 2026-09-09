#' Check Field Definitions Completeness
#'
#' Compares one or more datasets (CSV files) against a field definitions file
#' to identify:
#'   1. Columns that exist in the data but are undocumented in the field
#'      definitions file.
#'   2. Columns documented in the field definitions file but not found in the
#'      corresponding dataset.
#'   3. Dataset name mismatches between what was supplied and what appears in
#'      the field definitions file.
#'   4. Field definition rows with a missing/blank Definition and/or Units
#'      value.
#'
#' @param datasets A NAMED list of file paths (relative to the project root;
#'   resolved with here::here()). Names MUST match the values used in the
#'   'Dataset' column of the field definitions file.
#'   e.g. list(patients = "data/patients.csv", labs = "data/labs.csv")
#' @param field_definitions_path Path (relative to project root) to the
#'   xx_fieldDefinitions.csv file. Must contain columns: Dataset, Column_Name,
#'   Definition, Units.
#'
#' @return A list with:
#'   \item{actual_columns}{Every Dataset/Column_Name pair found in the loaded data}
#'   \item{defined_columns}{Every Dataset/Column_Name pair found in fieldDefinitions}
#'   \item{missing_from_defs}{Columns present in the data but NOT documented in fieldDefinitions}
#'   \item{missing_from_data}{Columns documented in fieldDefinitions but NOT found in the data}
#'   \item{datasets_only_in_defs}{Dataset names in fieldDefinitions with no matching entry in `datasets`}
#'   \item{datasets_only_in_data}{Dataset names in `datasets` with no matching entry in fieldDefinitions}
#'   \item{missing_info}{Rows of fieldDefinitions (for supplied datasets) with a blank Definition and/or Units}
#'   \item{field_defs}{The fieldDefinitions data as read in, for reference}
#'
#' @export
check_field_definitions <- function(datasets, field_definitions_path) {

  library(tidyverse)
  library(here)

  if (is.null(names(datasets)) || any(names(datasets) == "")) {
    stop("`datasets` must be a NAMED list, e.g. list(patients = 'data/patients.csv').")
  }

  # ---- Read in each dataset ----
  data_list <- purrr::map(datasets, function(path) {
    readr::read_csv(here::here(path), show_col_types = FALSE)
  })

  # ---- Every Dataset / Column_Name pair actually present in the data ----
  actual_columns <- purrr::map2_dfr(
    data_list, names(data_list),
    function(df, dataset_name) {
      tibble::tibble(Dataset = dataset_name, Column_Name = names(df))
    }
  )

  # ---- Read field definitions ----
  field_defs <- readr::read_csv(here::here(field_definitions_path), show_col_types = FALSE)

  required_cols <- c("Dataset", "Column_Name", "Definition", "Units")
  missing_req_cols <- setdiff(required_cols, names(field_defs))
  if (length(missing_req_cols) > 0) {
    stop(
      "The fieldDefinitions file is missing required column(s): ",
      paste(missing_req_cols, collapse = ", ")
    )
  }

  defined_columns <- field_defs |>
    dplyr::select(Dataset, Column_Name) |>
    dplyr::distinct()

  # ---- 1. Columns in the data but not documented in fieldDefinitions ----
  missing_from_defs <- dplyr::anti_join(
    actual_columns, defined_columns,
    by = c("Dataset", "Column_Name")
  )

  # ---- 2. Columns documented in fieldDefinitions but not found in the data ----
  # (only compare against datasets the user actually supplied to this call)
  defined_in_loaded <- defined_columns |>
    dplyr::filter(Dataset %in% names(datasets))

  missing_from_data <- dplyr::anti_join(
    defined_in_loaded, actual_columns,
    by = c("Dataset", "Column_Name")
  )

  # ---- Dataset-level name mismatches ----
  datasets_only_in_defs <- setdiff(unique(field_defs$Dataset), names(datasets))
  datasets_only_in_data <- setdiff(names(datasets), unique(field_defs$Dataset))

  # ---- 3. Missing Definition / Units values (blank or NA) ----
  missing_info <- field_defs |>
    dplyr::filter(Dataset %in% names(datasets)) |>
    dplyr::mutate(
      Definition_missing = is.na(Definition) | stringr::str_trim(Definition) == "",
      Units_missing       = is.na(Units) | stringr::str_trim(Units) == ""
    ) |>
    dplyr::filter(Definition_missing | Units_missing) |>
    dplyr::select(Dataset, Column_Name, Definition_missing, Units_missing)

  list(
    actual_columns        = actual_columns,
    defined_columns       = defined_columns,
    missing_from_defs     = missing_from_defs,
    missing_from_data     = missing_from_data,
    datasets_only_in_defs = datasets_only_in_defs,
    datasets_only_in_data = datasets_only_in_data,
    missing_info          = missing_info,
    field_defs            = field_defs
  )
}
