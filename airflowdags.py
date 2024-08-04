import os
import sys
import psycopg2
import traceback
import logging
import pandas as pd
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator

# Logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')

# PostgreSQL connection details
postgres_host = 'postgres'
postgres_database = 'geodatazone'
postgres_user = 'airflow'
postgres_password = 'airflow'
postgres_port = '5432'  # Default PostgreSQL port

# Set the path to your CSV file
csv_file_path = r'C:\\Users\\91990\\flask1\\airflow-docker\\dags\\in.csv'  # Use raw string for Windows path

# Create a connection to PostgreSQL
def create_postgres_connection():
    try:
        conn = psycopg2.connect(
            host=postgres_host,
            database=postgres_database,
            user=postgres_user,
            password=postgres_password,
            port=postgres_port
        )
        logging.info('Postgres server connection is successful')
        return conn
    except Exception as e:
        traceback.print_exc()
        logging.error("Couldn't create the Postgres connection")
        return None

def create_postgres_table(cur):
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cities (
                city VARCHAR(50) PRIMARY KEY,
                lat FLOAT,
                lng FLOAT,
                country VARCHAR(50),
                iso2 VARCHAR(2),
                admin_name VARCHAR(50),
                capital VARCHAR(20),
                population INTEGER,
                population_proper INTEGER
            )
        """)
        logging.info('New table cities created successfully in PostgreSQL server')
    except Exception as e:
        logging.warning(f'Check if the table cities exists: {e}')

def write_to_postgres(cur):
    df = pd.read_csv(csv_file_path)
    inserted_row_count = 0

    for _, row in df.iterrows():
        count_query = "SELECT COUNT(*) FROM cities WHERE city = %s"
        cur.execute(count_query, (row['city'],))
        result = cur.fetchone()

        if result[0] == 0:
            inserted_row_count += 1
            cur.execute("""
                INSERT INTO cities (city, lat, lng, country, iso2, admin_name, capital, population, population_proper) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(row['city']),
                float(row['lat']),
                float(row['lng']),
                str(row['country']),
                str(row['iso2']),
                str(row['admin_name']),
                str(row['capital']),
                int(row['population']),
                int(row['population_proper'])
            ))

    logging.info(f'{inserted_row_count} rows from CSV file inserted into cities table successfully')

def write_csv_to_postgres_main():
    conn = create_postgres_connection()
    if conn is None:
        return

    cur = conn.cursor()
    create_postgres_table(cur)
    write_to_postgres(cur)
    conn.commit()
    cur.close()
    conn.close()

# Setting the start date to 18-07-2024
start_date = datetime(2024, 7, 18, 12, 10)

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': start_date,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

# Creating the DAG
with DAG('csv_extract_airflow_docker', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:
    logging.info('CHECK 1')
     
    write_csv_to_postgres = PythonOperator(
        task_id='write_csv_to_postgres',
        python_callable=write_csv_to_postgres_main,
        retries=1,
        retry_delay=timedelta(seconds=15)
    )
    
    logging.info('CHECK 2')
    
write_csv_to_postgres