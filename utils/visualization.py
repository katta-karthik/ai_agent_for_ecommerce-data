import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def setup_plot_style():
    plt.style.use('dark_background')
    sns.set_palette("husl")
    plt.rcParams['figure.facecolor'] = '#0E1117'
    plt.rcParams['axes.facecolor'] = '#0E1117'
    plt.rcParams['text.color'] = 'white'
    plt.rcParams['axes.labelcolor'] = 'white'
    plt.rcParams['xtick.color'] = 'white'
    plt.rcParams['ytick.color'] = 'white'

def create_visualization(df, viz_type):
    if df.empty or len(df) <= 1:
        return None
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [col for col in numeric_cols if 'id' not in col.lower()]
    
    if not numeric_cols:
        return None
    
    main_metric = numeric_cols[0]
    
    try:
        setup_plot_style()
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#0E1117')
        
        if viz_type == "Bar Chart" and 'item_id' in df.columns:
            data = df.head(15).copy()
            bars = ax.bar(data['item_id'].astype(str), data[main_metric], 
                         color=plt.cm.viridis(np.linspace(0, 1, len(data))),
                         edgecolor='white', linewidth=0.8, alpha=0.9)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:,.0f}', ha='center', va='bottom',
                       fontsize=10, color='white', fontweight='bold')
            
            ax.set_xlabel('Product ID', fontsize=12, fontweight='bold')
            ax.set_ylabel(main_metric.replace('_', ' ').title(), fontsize=12, fontweight='bold')
            ax.set_title(f'{main_metric.replace("_", " ").title()} by Product', 
                        fontsize=16, fontweight='bold', pad=20)
            plt.xticks(rotation=45)
            
        elif viz_type == "Pie Chart" and len(df) <= 10:
            data = df.head(8).copy()
            colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
            ax.pie(data[main_metric], 
                  labels=[f'Product {x}' for x in data['item_id']], 
                  autopct='%1.1f%%',
                  colors=colors,
                  startangle=90,
                  textprops={'fontsize': 10, 'color': 'white'})
            
            ax.set_title(f'Distribution of {main_metric.replace("_", " ").title()}', 
                        fontsize=16, fontweight='bold', pad=20)
            
        else:
            plt.close(fig)
            return None
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        plt.close(fig)
        return None

def get_visualization_options(df):
    if df.empty or len(df) <= 1:
        return []
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return []
    
    options = []
    
    if len(df) > 1:
        options.append("Bar Chart")
    
    if 2 <= len(df) <= 10:
        options.append("Pie Chart")
    
    return options
