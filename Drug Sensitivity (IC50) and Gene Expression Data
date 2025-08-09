# Load required libraries
library(readxl)
library(tidyverse)
library(PharmacoGx)
library(rio)

# ------------------------------
# Download and load GDSC dose-response data (IC50)
# ------------------------------

# URLs for the GDSC drug response Excel files
url_gdsc2 <- "https://cog.sanger.ac.uk/cancerrxgene/GDSC_release8.5/GDSC2_fitted_dose_response_27Oct23.xlsx"
url_gdsc1 <- "https://cog.sanger.ac.uk/cancerrxgene/GDSC_release8.5/GDSC1_fitted_dose_response_27Oct23.xlsx"

# Temporary file paths to save downloaded files
local_gdsc2 <- tempfile(fileext = ".xlsx")
local_gdsc1 <- tempfile(fileext = ".xlsx")

# Download the Excel files in binary mode
download.file(url_gdsc2, destfile = local_gdsc2, mode = "wb")
download.file(url_gdsc1, destfile = local_gdsc1, mode = "wb")

# Read the Excel files into data frames
pancancerIC50_GDSC2 <- read_excel(local_gdsc2)
pancancerIC50_GDSC1 <- read_excel(local_gdsc1)

# ------------------------------
# Extract gene expression data from PharmacoGx GDSC dataset
# ------------------------------

# Display available pharmacogenomic datasets
availablePSets()

# Download the GDSC pharmacogenomic dataset (version 2020)
GDSC <- downloadPSet("GDSC_2020(v2-8.2)")

# Extract RNA expression data as SummarizedExperiment object
GDSC_expression <- summarizeMolecularProfiles(GDSC, mDataType = "rna")

# Convert SummarizedExperiment to expression matrix (genes x samples)
gene_expression_matrix <- assay(GDSC_expression)

# Convert matrix to data frame, transpose so samples are rows and genes are columns
DEx_data <- as.data.frame(t(gene_expression_matrix))

# Add cell line names as a column
DEx_data$CellLine <- rownames(DEx_data)

# Reorder columns to have CellLine as first column
DEx_data <- DEx_data[, c("CellLine", setdiff(names(DEx_data), "CellLine"))]

# View first few rows of gene expression data
head(DEx_data)

# ------------------------------
# Filter IC50 data for a specific drug and prepare for merging
# ------------------------------

# Set the drug name of interest here (change as needed)
selected_drug <- "DrugName"  # Replace "DrugName" with the actual drug name

# Filter IC50 data for the selected drug
drug_IC50 <- filter(pancancerIC50_GDSC2, DRUG_NAME == selected_drug)

# ------------------------------
# Clean cell line names to standardize before merging
# ------------------------------

# Function to clean cell line names: remove hyphens, spaces, slashes and uppercase
clean_cell_line_names <- function(x) {
  x <- gsub("[- /]", "", x)
  toupper(x)
}

# Apply cleaning to IC50 data cell line names
drug_IC50_clean <- drug_IC50
drug_IC50_clean$Cell.Line.Name <- clean_cell_line_names(drug_IC50_clean$Cell.Line.Name)

# Apply cleaning to gene expression data cell line names
DEx_data_clean <- DEx_data
DEx_data_clean$CellLine <- clean_cell_line_names(DEx_data_clean$CellLine)

# ------------------------------
# Merge cleaned gene expression and IC50 data by cell line names
# ------------------------------

merged_data <- DEx_data_clean %>%
  inner_join(drug_IC50_clean, by = c("CellLine" = "CELL_LINE_NAME "))

# ------------------------------
# Remove unnecessary columns to keep relevant data only
# ------------------------------

final_data <- merged_data %>%
  select(-c(DATASET, NLME_RESULT_ID, NLME_CURVE_ID, COSMIC_ID, CELL_LINE_NAME, SANGER_MODEL_ID,
            TCGA_DESC, DRUG_ID, DRUG_NAME, PUTATIVE_TARGET, PATHWAY_NAME, COMPANY_ID,
            WEBRELEASE, MIN_CONC, MAX_CONC, AUC, RMSE, Z_SCORE))

# ------------------------------
# Export final merged data to CSV
# ------------------------------

export(final_data, paste0("path/to/save/", selected_drug, "_GEx_IC50.csv"))  # Modify path as needed
