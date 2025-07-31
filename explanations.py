def generate_explanation(df, search_query):
    if df.empty:
        return "No data found for your query."

    row_count = len(df)
    col_count = len(df.columns)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()

    if row_count == 1:
        row = df.iloc[0]
        details = []
        for col in df.columns:
            val = row[col]
            if col in numeric_cols:
                details.append(f"{col.replace('_',' ').title()}: {val:,.2f}")
            else:
                details.append(f"{col.replace('_',' ').title()}: {val}")
        return f"Here are the details: {', '.join(details)}."
    elif row_count > 1:
    
        summary = []
        if numeric_cols:
            for col in numeric_cols:
                col_data = df[col]
                summary.append(f"{col.replace('_',' ').title()} (min: {col_data.min():,.2f}, max: {col_data.max():,.2f}, avg: {col_data.mean():,.2f})")
        if text_cols:
            for col in text_cols:
                unique_vals = df[col].nunique()
                summary.append(f"{col.replace('_',' ').title()} ({unique_vals} unique values)")
        if summary:
            return f"Found {row_count} records. Key stats: {', '.join(summary)}."
        else:
            return f"Found {row_count} records."
    else:
        return f"Found {row_count} records for your query."
