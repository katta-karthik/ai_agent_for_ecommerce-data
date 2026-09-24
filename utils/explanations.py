"""Statistical summary and explanation utilities for query results."""

import pandas as pd


def generate_explanation(df: pd.DataFrame, search_query: str) -> str:
    """Generate business-oriented text summary from query results DataFrame."""
    if df is None or df.empty:
        return "No matching data found for this question."

    row_count = len(df)
    cols = list(df.columns)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    if row_count == 1:
        row = df.iloc[0]
        details = []
        for col in cols:
            val = row[col]
            clean_name = col.replace('_', ' ').title()
            if isinstance(val, (int, float)):
                if 'sales' in col.lower() or 'revenue' in col.lower() or 'spend' in col.lower() or 'cpc' in col.lower():
                    details.append(f"**{clean_name}**: ${val:,.2f}")
                elif 'pct' in col.lower() or 'ctr' in col.lower():
                    details.append(f"**{clean_name}**: {val:.2f}%")
                elif 'roas' in col.lower():
                    details.append(f"**{clean_name}**: {val:.2f}x")
                else:
                    details.append(f"**{clean_name}**: {val:,.0f}")
            else:
                details.append(f"**{clean_name}**: {val}")
        return f"Summary: {', '.join(details)}."

    # Multi-row summary
    summary_parts = []
    for col in numeric_cols:
        if 'id' in col.lower() or 'rank' in col.lower():
            continue
        col_data = df[col].dropna()
        if not col_data.empty:
            clean_name = col.replace('_', ' ').title()
            total = col_data.sum()
            avg = col_data.mean()
            maximum = col_data.max()
            if 'sales' in col.lower() or 'spend' in col.lower():
                summary_parts.append(f"**Total {clean_name}**: ${total:,.2f} (Avg: ${avg:,.2f}, Max: ${maximum:,.2f})")
            elif 'roas' in col.lower():
                summary_parts.append(f"**Avg {clean_name}**: {avg:.2f}x (Peak: {maximum:.2f}x)")
            else:
                summary_parts.append(f"**Avg {clean_name}**: {avg:,.1f}")

    metric_summary = " | ".join(summary_parts[:3]) if summary_parts else ""
    return f"Retrieved **{row_count}** records matching your query. {metric_summary}"
