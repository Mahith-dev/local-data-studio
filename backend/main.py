import io
import re
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI(title="Local Data Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_data = {
    "df": None,
    "files": [],
    "notes": []
}

def load_tabular_file(contents: bytes, filename: str) -> pd.DataFrame:
    """Robustly loads a CSV/TSV with automatic delimiter and encoding detection."""
    text = contents.decode('utf-8', errors='replace')

    # Check common delimiters: semicolon vs comma vs tab
    first_lines = "".join(text.splitlines(keepends=True)[:5])
    if ';' in first_lines and first_lines.count(';') > first_lines.count(','):
        sep = ';'
    elif '\t' in first_lines and first_lines.count('\t') > first_lines.count(','):
        sep = '\t'
    else:
        sep = ','

    return pd.read_csv(io.StringIO(text), sep=sep)

@app.get("/api/health")
def health_check():
    return {"status": "running"}

@app.post("/api/upload")
async def upload_datasets(files: List[UploadFile] = File(...)):
    parsed_dfs = []
    loaded_filenames = []
    metadata_notes = []

    for file in files:
        contents = await file.read()
        name_lower = file.filename.lower()

        # Handle metadata/names documentation files without crashing
        if name_lower.endswith(('.names', '.txt', '.md', '.json')):
            metadata_notes.append(f"Loaded metadata doc: {file.filename}")
            continue

        try:
            df_temp = load_tabular_file(contents, file.filename)

            # Tag the source domain from the filename (e.g. 'red' or 'white')
            clean_tag = re.sub(r'winequality[-_]?|\.csv$', '', file.filename, flags=re.IGNORECASE)
            clean_tag = clean_tag.strip(" -_") or file.filename
            df_temp['source_file'] = clean_tag

            parsed_dfs.append(df_temp)
            loaded_filenames.append(file.filename)
        except Exception as e:
            metadata_notes.append(f"Skipped {file.filename}: {str(e)}")

    if not parsed_dfs:
        return {"error": "No valid tabular data found in uploaded files."}

    # If multiple files are uploaded with the same columns, merge them
    if len(parsed_dfs) == 1:
        merged_df = parsed_dfs[0]
    else:
        # Check if feature columns match (excluding the newly added 'source_file')
        base_cols = [c for c in parsed_dfs[0].columns if c != 'source_file']
        compatible = all(
            [c for c in df_i.columns if c != 'source_file'] == base_cols
            for df_i in parsed_dfs[1:]
        )
        if compatible:
            merged_df = pd.concat(parsed_dfs, ignore_index=True)
            metadata_notes.append(f"Auto-merged {len(parsed_dfs)} compatible datasets into one unified dataset.")
        else:
            # Fallback to the largest dataset if columns differ
            merged_df = max(parsed_dfs, key=lambda x: len(x))
            metadata_notes.append("Uploaded datasets had different columns; loaded primary dataset.")

    current_data["df"] = merged_df
    current_data["files"] = loaded_filenames
    current_data["notes"] = metadata_notes

    return {
        "files_loaded": loaded_filenames,
        "notes": metadata_notes,
        "rows": int(merged_df.shape[0]),
        "columns": int(merged_df.shape[1]),
        "column_names": list(merged_df.columns),
        "missing_cells": int(merged_df.isnull().sum().sum()),
        "numerical_columns": list(merged_df.select_dtypes(include=['number']).columns),
        "categorical_columns": list(merged_df.select_dtypes(exclude=['number']).columns),
    }