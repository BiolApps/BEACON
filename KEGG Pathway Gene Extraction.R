# Load required libraries (install if missing)
required_packages <- c("KEGGREST", "dplyr", "tidyr", "org.Hs.eg.db", "rio")
for(pkg in required_packages){
  if(!requireNamespace(pkg, quietly = TRUE)){
    install.packages(pkg)
  }
  library(pkg, character.only = TRUE)
}

# ----------- Parameters -----------

# KEGG pathway ID (replace as needed)
pathway_id <- "hsa04012"  # Example: ErbB signaling pathway (EGFR)

# Input data file containing merged gene expression and drug IC50 data
input_data_file <- "DrugName_GEx_IC50.csv"

# Output file name for pathway gene subset
output_file <- paste0("DrugName_GEx_", pathway_id, "_subset.csv")


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


# ----------- Load merged gene expression and drug response data -----------

GEx_full <- read.csv(input_data_file)


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


# ----------- Export the subsetted data -----------

export(GEx_pathway_subset, output_file)

message("Subset data exported to: ", output_file)
