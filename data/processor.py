import pandas as pd
import sqlite3
import os

class EcommerceDataProcessor:
    def __init__(self, db_name="ecommerce_optimized.db"):
        self.db_name = db_name
        self.conn = None
    
    def connect_db(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn
    
    def analyze_csv_files(self):
        print("Analyzing CSV data...")
        
        files = {
            'total_sales': 'data/total_sales.csv',
            'ad_sales': 'data/ad_sales.csv', 
            'eligibility': 'data/eligibility.csv'
        }
        
        analysis = {}
        
        for name, path in files.items():
            df = pd.read_csv(path)
            print(f"{name}: {df.shape[0]} rows, {df.shape[1]} columns")
            
            analysis[name] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict()
            }
        
        return analysis
    
    def create_optimized_tables(self):
        print("Creating database tables...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS daily_sales") 
        cursor.execute("DROP TABLE IF EXISTS daily_ad_performance")
        cursor.execute("DROP TABLE IF EXISTS product_eligibility")
        
        cursor.execute("""
        CREATE TABLE products (
            item_id INTEGER PRIMARY KEY,
            first_sale_date DATE,
            last_sale_date DATE,
            total_lifetime_sales DECIMAL(10,2),
            total_lifetime_ad_sales DECIMAL(10,2),
            is_currently_eligible BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE daily_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            item_id INTEGER NOT NULL,
            total_sales DECIMAL(10,2) DEFAULT 0,
            total_units_ordered INTEGER DEFAULT 0,
            FOREIGN KEY (item_id) REFERENCES products(item_id),
            UNIQUE(date, item_id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE daily_ad_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            item_id INTEGER NOT NULL,
            ad_sales DECIMAL(10,2) DEFAULT 0,
            ad_spend DECIMAL(10,2) DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            units_sold INTEGER DEFAULT 0,
            roas DECIMAL(8,2),
            cpc DECIMAL(8,2),
            ctr DECIMAL(8,4),
            FOREIGN KEY (item_id) REFERENCES products(item_id),
            UNIQUE(date, item_id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE product_eligibility (
            item_id INTEGER PRIMARY KEY,
            eligibility_datetime_utc TIMESTAMP,
            is_eligible BOOLEAN,
            message TEXT,
            FOREIGN KEY (item_id) REFERENCES products(item_id)
        )
        """)
        
        conn.commit()
        print("Tables created successfully.")
        
    def load_and_transform_data(self):
        print("Loading data...")
        
        conn = self.connect_db()
        
        df_sales = pd.read_csv('data/total_sales.csv')
        df_sales.to_sql('daily_sales', conn, if_exists='append', index=False)
        
        df_ads = pd.read_csv('data/ad_sales.csv')
        
        df_ads['roas'] = df_ads['ad_sales'] / df_ads['ad_spend'].replace(0, float('inf'))
        df_ads['roas'] = df_ads['roas'].replace([float('inf'), float('-inf')], 0)
        
        df_ads['cpc'] = df_ads['ad_spend'] / df_ads['clicks'].replace(0, float('inf'))
        df_ads['cpc'] = df_ads['cpc'].replace([float('inf'), float('-inf')], 0)
        
        df_ads['ctr'] = df_ads['clicks'] / df_ads['impressions'].replace(0, float('inf'))
        df_ads['ctr'] = df_ads['ctr'].replace([float('inf'), float('-inf')], 0)
        
        df_ads.to_sql('daily_ad_performance', conn, if_exists='append', index=False)
        
        df_eligibility = pd.read_csv('data/eligibility.csv')
        df_eligibility['is_eligible'] = df_eligibility['eligibility'] == 'TRUE'
        df_eligibility = df_eligibility.drop('eligibility', axis=1)
        df_eligibility = df_eligibility.sort_values('eligibility_datetime_utc').groupby('item_id').last().reset_index()
        df_eligibility.to_sql('product_eligibility', conn, if_exists='append', index=False)
        
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO products (item_id, first_sale_date, last_sale_date, total_lifetime_sales, total_lifetime_ad_sales, is_currently_eligible)
        SELECT 
            all_items.item_id,
            MIN(all_items.date) as first_sale_date,
            MAX(all_items.date) as last_sale_date,
            COALESCE(s.total_sales, 0) as total_lifetime_sales,
            COALESCE(a.total_ad_sales, 0) as total_lifetime_ad_sales,
            COALESCE(e.is_eligible, 0) as is_currently_eligible
        FROM (
            SELECT item_id, date FROM daily_sales
            UNION 
            SELECT item_id, date FROM daily_ad_performance
        ) all_items
        LEFT JOIN (SELECT item_id, SUM(total_sales) as total_sales FROM daily_sales GROUP BY item_id) s ON all_items.item_id = s.item_id
        LEFT JOIN (SELECT item_id, SUM(ad_sales) as total_ad_sales FROM daily_ad_performance GROUP BY item_id) a ON all_items.item_id = a.item_id
        LEFT JOIN product_eligibility e ON all_items.item_id = e.item_id
        GROUP BY all_items.item_id, s.total_sales, a.total_ad_sales, e.is_eligible
        """)
        
        conn.commit()
        print("Data loaded successfully.")
        
    def run_full_pipeline(self):
        print("Starting data processing...")
        
        analysis = self.analyze_csv_files()
        self.create_optimized_tables()
        self.load_and_transform_data()
        
        print("Database ready for AI agent.")
        return analysis

if __name__ == "__main__":
    processor = EcommerceDataProcessor()
    processor.run_full_pipeline()
