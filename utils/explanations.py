def generate_explanation(df, search_query):
    if df.empty:
        return "No data found for your query."
    
    row_count = len(df)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if "total sales" in search_query.lower():
        if row_count == 1:
            total = df.iloc[0, 0]
            return f"Your business has generated **${total:,.2f}** in total sales."
        else:
            sales_cols = [col for col in numeric_cols if 'sales' in col.lower()]
            if sales_cols:
                total = df[sales_cols[0]].sum()
                top_product = df.iloc[0]['item_id'] if 'item_id' in df.columns else "N/A"
                return f"Found **{row_count} products** with total sales of **${total:,.2f}**. Top performer: Product {top_product}."
    
    elif "calculate" in search_query.lower() and "roas" in search_query.lower():
        if row_count == 1:
            avg_roas = df.iloc[0, 0]
            return f"Average Return on Ad Spend is **{avg_roas:.2f}x**. For every $1 spent on advertising, you generate ${avg_roas:.2f} in revenue."
        else:
            avg_roas = df[numeric_cols[0]].mean() if numeric_cols else 0
            return f"Calculated average RoAS: **{avg_roas:.2f}x** across {len(df)} products."
    
    elif "roas" in search_query.lower():
        if row_count == 1:
            roas = df.iloc[0, 0]
            return f"Return on Ad Spend is **{roas:.2f}x**."
        else:
            avg_roas = df[numeric_cols[0]].mean() if numeric_cols else 0
            max_roas = df[numeric_cols[0]].max() if numeric_cols else 0
            return f"Analyzed {row_count} products. Average RoAS: **{avg_roas:.2f}x**, Best: **{max_roas:.2f}x**."
    
    elif "click-through rate" in search_query.lower() or "ctr" in search_query.lower():
        if row_count == 1:
            ctr_value = df.iloc[0, 1] if len(df.columns) > 1 else df.iloc[0, 0]
            return f"Highest Click-Through Rate: **{ctr_value*100:.2f}%**."
        else:
            ctr_col = [col for col in numeric_cols if 'ctr' in col.lower()]
            if ctr_col:
                max_ctr = df[ctr_col[0]].max()
                top_product = df.iloc[0]['item_id'] if 'item_id' in df.columns else "N/A"
                return f"Product **{top_product}** has highest CTR: **{max_ctr*100:.2f}%**."
    
    elif "top" in search_query.lower() and row_count > 1:
        sales_cols = [col for col in numeric_cols if 'sales' in col.lower()]
        main_col = sales_cols[0] if sales_cols else numeric_cols[0]
        top_product = df.iloc[0]['item_id'] if 'item_id' in df.columns else "N/A"
        top_value = df.iloc[0][main_col]
        return f"Top {row_count} products. Leader: Product **{top_product}** with **${top_value:,.2f}**."
    
    elif "average revenue" in search_query.lower():
        if row_count == 1:
            avg_revenue = df.iloc[0, 0]
            return f"Average revenue per product: **${avg_revenue:,.2f}**."
        else:
            sales_cols = [col for col in numeric_cols if 'sales' in col.lower()]
            if sales_cols:
                avg_revenue = df[sales_cols[0]].mean()
                return f"Average revenue: **${avg_revenue:,.2f}** across {len(df)} products."
    
    else:
        return f"Retrieved **{row_count} records** for analysis."
