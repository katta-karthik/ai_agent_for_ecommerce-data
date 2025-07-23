from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

class EcommerceAIAgent:
    def __init__(self, db_path="ecommerce_optimized.db"):
        load_dotenv()
        self.db_path = db_path
        self.setup_components()
        
    def setup_components(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            print("⚠️  WARNING: GROQ_API_KEY not found in .env file")
            print("   Create a .env file with: GROQ_API_KEY=your_key_here")
        
        self.llm = ChatGroq(
            model_name="llama-3.1-8b-instant", 
            temperature=0,
            max_tokens=150,
            groq_api_key=groq_api_key
        )
        
        self.db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")
        
        sql_prompt = PromptTemplate(
            input_variables=["input", "table_info", "dialect"],
            template="""Given an input question, create a syntactically correct {dialect} query to run.

DATABASE SCHEMA:
{table_info}

INSTRUCTIONS:
1. Only use tables and columns that exist in the schema
2. Use aggregate functions (SUM, AVG, COUNT) appropriately
3. For "top" queries, use ORDER BY with LIMIT
4. For averages, use AVG() function
5. Use proper column names from schema
6. Return ONLY the raw SQL query - NO markdown, NO explanations, NO formatting

Question: {input}
SQLQuery:"""
        )
        
        self.sql_chain = SQLDatabaseChain.from_llm(
            llm=self.llm,
            db=self.db,
            prompt=sql_prompt,
            verbose=False,
            return_intermediate_steps=True
        )
    
    def query_database(self, question: str):
        try:
            result = self.sql_chain({"query": question})
           
            sql_query = ""
            if 'intermediate_steps' in result and result['intermediate_steps']:
             
                if len(result['intermediate_steps']) > 0:
                    sql_query = result['intermediate_steps'][0].get('sql_cmd', '')
        
            if not sql_query:
                sql_query = result.get('result', '')
            
            sql_query = self.clean_sql_query(sql_query)
            
            if sql_query and sql_query.strip().upper().startswith('SELECT'):
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql_query(sql_query, conn)
                conn.close()
                
                return {
                    'question': question,
                    'sql': sql_query,
                    'results': df,
                    'row_count': len(df)
                }
            else:
                return {'error': f"Invalid SQL generated: {sql_query}"}
                
        except Exception as e:
            return {'error': str(e)}
    
    def clean_sql_query(self, sql_text: str) -> str:
        """Clean SQL query by removing markdown formatting and extra whitespace"""
        if not sql_text:
            return ""
     
        sql_text = sql_text.replace("```sql", "").replace("```", "")
        sql_text = sql_text.replace("```SQL", "").replace("SQL:", "").replace("SQLQuery:", "")
        
       
        sql_text = " ".join(sql_text.split())
        
        
        sql_text = sql_text.strip()
        
        return sql_text
