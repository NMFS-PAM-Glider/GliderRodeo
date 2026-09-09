# Field Definitions Completeness Check

Checks whether every column in your datasets is documented in a field
definitions file, and whether each documented field has a complete
`Definition` and `Units` value.

## Folder structure

```
field_def_check/
├── R/
│   └── check_field_definitions.R   # the core function
├── data/
│   ├── patients.csv                # demo dataset
│   ├── labs.csv                    # demo dataset
│   └── xx_fieldDefinitions.csv     # demo field definitions file
├── field_definitions_report.Rmd    # knit this to get the HTML report
└── README.md
```

Open this whole folder as an RStudio Project (or just make sure your working
directory is this folder) so that `here::here()` resolves paths correctly.

## Requirements

```r
install.packages(c("tidyverse", "here", "rmarkdown", "DT"))
```

## Try it with the demo data

Just knit `field_definitions_report.Rmd` as-is (Knit button, or
`rmarkdown::render("field_definitions_report.Rmd")`). The bundled demo data
intentionally contains a few gaps so you can see what each section of the
report catches:

- `patients.csv` has a `height_cm` column with no matching row in
  `xx_fieldDefinitions.csv` → shows up under **"Columns Missing From
  fieldDefinitions."**
- `xx_fieldDefinitions.csv` documents a `bmi` column for the `labs` dataset
  that doesn't actually exist in `labs.csv` → shows up under **"Columns
  Missing From the Data."**
- The `patient_id` rows have blank `Units`, and the `sex` row has both a
  blank `Definition` and blank `Units` → shows up under **"Missing
  Definition / Units."**

## Using your own data

1. Replace the CSVs in `data/` with your own (or point to wherever your
   files live).
2. Make sure your `xx_fieldDefinitions.csv` has (at minimum) these four
   columns: `Dataset`, `Column_Name`, `Definition`, `Units`.
3. In `field_definitions_report.Rmd`, edit the `inputs` chunk:

   ```r
   datasets <- list(
     patients = "data/patients.csv",
     labs     = "data/labs.csv"
     # add as many datasets as you need — the list name must match the
     # value used in the 'Dataset' column of your fieldDefinitions file
   )

   field_definitions_path <- "data/xx_fieldDefinitions.csv"
   ```

4. Knit the report.

## Using the function directly (without the Rmd)

```r
source(here::here("R", "check_field_definitions.R"))

results <- check_field_definitions(
  datasets = list(
    patients = "data/patients.csv",
    labs     = "data/labs.csv"
  ),
  field_definitions_path = "data/xx_fieldDefinitions.csv"
)

results$missing_from_defs   # columns in the data, undocumented
results$missing_from_data   # columns documented, not found in data
results$missing_info        # rows with blank Definition and/or Units
results$datasets_only_in_defs
results$datasets_only_in_data
```

## Notes on how matching works

- Matching is done on the pair `(Dataset, Column_Name)` — a column is only
  considered "documented" if there's a row in fieldDefinitions with the
  exact same Dataset name and Column_Name (case-sensitive, no trimming
  applied automatically).
- `missing_from_data` and the `Definition`/`Units` completeness check only
  look at datasets you actually pass into `datasets` — if your
  fieldDefinitions file covers other datasets you didn't load, those are
  reported separately under `datasets_only_in_defs` rather than flagged as
  missing columns.
- Both blank strings (`""` or whitespace-only) and `NA` values count as
  "missing" for `Definition` and `Units`.
