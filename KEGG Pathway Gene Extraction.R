# ------------------------------------------------------------
# Script: Subset merged gene expression and IC50 data by KEGG pathway
#
# Description:
# This script retrieves all genes associated with a selected KEGG pathway,
# maps them to Ensembl gene IDs, and subsets a merged dataset of gene
# expression and drug response (IC50) values to include only those genes.
# It then exports the subsetted dataset for downstream pathway-specific
# analysis.
#
# Main steps:
#   1. Load or install required R packages.
#   4. Load merged gene expression and IC50 dataset.
#   3. Retrieve KEGG pathway genes and clean gene symbols.
#   4. Map gene symbols to Ensembl IDs using org.Hs.eg.db.
#   5. Subset dataset to pathway genes + response variable.
#   6. Identify missing pathway genes in the dataset.
#   7. Export subsetted dataset to CSV.
# ------------------------------------------------------------


# ----------- Load required libraries (install if missing) -----------
required_packages <- c("KEGGREST", "dplyr", "tidyr", "org.Hs.eg.db", "rio")

# Install missing packages
installed <- required_packages %in% installed.packages()[, "Package"]
if (any(!installed)) {
  install.packages(required_packages[!installed])
}

# Load all packages
lapply(required_packages, library, character.only = TRUE)


# ----------- Parameters -----------

# KEGG pathway ID (replace as needed)
pathway_id <- "hsa04012"  # Example: ErbB signaling pathway (EGFR)

# Load combined gene expression and drug response data
# This file (DrugName_GEx_IC50.csv) is generated from the pipeline:
# "Drug Sensitivity (IC50) and Gene Expression Data.R" for each drug
# It contains merged data of gene expression profiles and IC50 values for the drug of interest.
GEx_full <- read.csv("DrugName_GEx_IC50.csv")


# ----------- Retrieve genes from the KEGG pathway -----------

genes <- keggGet(pathway_id)[[1]]$GENE
gene_symbols <- genes[seq(2, length(genes), 2)]
gene_symbols_df <- data.frame(gene_symbols)

gene_symbols_clean <- gene_symbols_df %>%
  mutate(gene_symbols = sub(";.*", "", gene_symbols))

unique_symbols <- unique(gene_symbols_clean$gene_symbols)
ensembl_ids <- mapIds(
  org.Hs.eg.db,
  keys = unique_symbols,
  column = "ENSEMBL",
  keytype = "SYMBOL",
  multiVals = "first"
)

gene_symbols_clean$ensembl_id <- ensembl_ids[gene_symbols_clean$gene_symbols]


# ----------- Extract relevant gene expression columns -----------

common_columns <- intersect(colnames(GEx_full), gene_symbols_clean$ensembl_id)
final_columns <- c(common_columns, tail(colnames(GEx_full), 1))

GEx_pathway_subset <- GEx_full[, final_columns, drop = FALSE]

missing_genes <- setdiff(gene_symbols_clean$ensembl_id, colnames(GEx_full))

if(length(missing_genes) > 0){
  message("Warning: The following pathway genes were not found in the expression dataset:")
  print(missing_genes)
} else {
  message("All pathway genes were found in the expression dataset.")
}


# --- Export the subsetted data ---

# Export to CSV (update path as needed)
export(GEx_pathway_subset, "DrugName_GEx_pathway.csv")

message("Subset data exported to: ", output_file)
