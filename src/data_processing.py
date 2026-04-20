# Data processing functions
import pandas as pd
import chardet

def format_display_name(name):
    if pd.isna(name):
        return "Unknown"
    name = str(name).strip()
    if ',' in name:
        parts = [part.strip() for part in name.split(',')]
        if len(parts) >= 2:
            return f"{parts[1]} {parts[0]}"
    return name

def load_and_combine_files(uploaded_files):
    dfs = []
    for uploaded_file in uploaded_files:
        try:
            # Try reading with default encoding first
            df = pd.read_csv(uploaded_file, encoding='latin1')
            dfs.append(df)
        except UnicodeDecodeError:
            # If encoding error, detect encoding and try again
            raw_data = uploaded_file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            uploaded_file.seek(0)  # Reset file pointer
            df = pd.read_csv(uploaded_file, encoding=encoding)
            dfs.append(df)

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    return pd.DataFrame()