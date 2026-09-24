"""Enhanced Matplotlib & Seaborn visualization utilities with dark theme."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


def setup_plot_style():
    """Configure modern dark theme matching Streamlit's default dark canvas."""
    plt.style.use('dark_background')
    sns.set_palette("husl")
    plt.rcParams['figure.facecolor'] = '#0E1117'
    plt.rcParams['axes.facecolor'] = '#0E1117'
    plt.rcParams['text.color'] = '#FAFAFA'
    plt.rcParams['axes.labelcolor'] = '#E0E0E0'
    plt.rcParams['xtick.color'] = '#B0B0B0'
    plt.rcParams['ytick.color'] = '#B0B0B0'
    plt.rcParams['grid.color'] = '#262730'
    plt.rcParams['grid.alpha'] = 0.5


def find_category_and_metric(df: pd.DataFrame):
    """Detect the most sensible category (x-axis) and metric (y-axis) columns."""
    if df.empty:
        return None, None

    cols = list(df.columns)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    non_numeric_cols = [c for c in cols if c not in numeric_cols]

    # Category candidate
    category_col = None
    if non_numeric_cols:
        category_col = non_numeric_cols[0]
    elif 'item_id' in cols:
        category_col = 'item_id'
    elif 'date' in cols:
        category_col = 'date'
    elif 'month' in cols:
        category_col = 'month'
    elif numeric_cols:
        category_col = numeric_cols[0]

    # Metric candidate
    metric_cols = [c for c in numeric_cols if c != category_col and 'id' not in c.lower() and 'rank' not in c.lower()]
    if not metric_cols and numeric_cols:
        metric_cols = [c for c in numeric_cols if c != category_col]

    metric_col = metric_cols[0] if metric_cols else (numeric_cols[0] if numeric_cols else None)

    return category_col, metric_col


def create_visualization(df: pd.DataFrame, viz_type: str):
    """Generate high-contrast, publication-quality matplotlib chart."""
    if df is None or df.empty or len(df) < 1:
        return None

    # Single scalar does not need chart
    if len(df) == 1 and len(df.columns) <= 2:
        return None

    category_col, metric_col = find_category_and_metric(df)
    if not metric_col:
        return None

    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=100)
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    try:
        data = df.head(15).copy()

        # Format labels
        if category_col and category_col in data.columns:
            data['x_label'] = data[category_col].astype(str)
        else:
            data['x_label'] = [f"Item {i+1}" for i in range(len(data))]

        x_vals = data['x_label']
        y_vals = pd.to_numeric(data[metric_col], errors='coerce').fillna(0)

        metric_name = metric_col.replace('_', ' ').title()
        cat_name = (category_col or 'Entity').replace('_', ' ').title()

        viz_type_lower = (viz_type or "").lower()

        if "bar" in viz_type_lower:
            colors = plt.cm.viridis(np.linspace(0.2, 0.85, len(data)))
            bars = ax.bar(x_vals, y_vals, color=colors, edgecolor='#4A4A5A', linewidth=0.8, alpha=0.9)

            # Data labels
            for bar in bars:
                height = bar.get_height()
                label = f"{height:,.0f}" if height >= 10 else f"{height:,.2f}"
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    label,
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    color='#FAFAFA',
                    fontweight='bold',
                )

            ax.set_title(f"{metric_name} by {cat_name}", fontsize=14, fontweight='bold', pad=15)
            ax.set_xlabel(cat_name, fontsize=11, fontweight='bold')
            ax.set_ylabel(metric_name, fontsize=11, fontweight='bold')
            plt.xticks(rotation=40, ha='right')

        elif "line" in viz_type_lower:
            ax.plot(x_vals, y_vals, color='#4CAF50', marker='o', linewidth=2.5, markersize=6, label=metric_name)
            ax.fill_between(x_vals, y_vals, color='#4CAF50', alpha=0.15)
            
            for x, y in zip(x_vals, y_vals):
                label = f"{y:,.0f}" if y >= 10 else f"{y:,.2f}"
                ax.text(x, y, label, ha='center', va='bottom', fontsize=8, color='#FAFAFA', fontweight='bold')

            ax.set_title(f"{metric_name} Trend Over Time", fontsize=14, fontweight='bold', pad=15)
            ax.set_xlabel(cat_name, fontsize=11, fontweight='bold')
            ax.set_ylabel(metric_name, fontsize=11, fontweight='bold')
            plt.xticks(rotation=40, ha='right')
            ax.grid(True, linestyle='--', alpha=0.3)

        elif "pie" in viz_type_lower and len(data) <= 10:
            colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
            ax.pie(
                y_vals,
                labels=[f"{l}" for l in x_vals],
                autopct='%1.1f%%',
                colors=colors,
                startangle=140,
                textprops={'fontsize': 10, 'color': '#FAFAFA'},
            )
            ax.set_title(f"Distribution of {metric_name}", fontsize=14, fontweight='bold', pad=15)

        else:
            # Default fallback to bar chart
            colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(data)))
            ax.bar(x_vals, y_vals, color=colors, edgecolor='#4A4A5A', linewidth=0.8)
            ax.set_title(f"{metric_name} by {cat_name}", fontsize=14, fontweight='bold', pad=15)
            plt.xticks(rotation=40, ha='right')

        plt.tight_layout()
        return fig
    except Exception as e:
        plt.close(fig)
        return None


def get_visualization_options(df: pd.DataFrame):
    """Return applicable chart types based on dataframe structure."""
    if df is None or df.empty or len(df) <= 1:
        return []

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return []

    options = ["Bar Chart"]
    
    # If date or month in columns, line chart makes sense
    date_cols = [c for c in df.columns if any(k in c.lower() for k in ['date', 'month', 'day', 'time', 'year'])]
    if date_cols or len(df) >= 3:
        options.append("Line Chart")

    if 2 <= len(df) <= 8:
        options.append("Pie Chart")

    return options
