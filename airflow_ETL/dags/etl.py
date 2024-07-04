from airflow import DAG
import json
import pandas as pd
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.http.operators.http import HttpOperator

def data_transformation(ti):
    raw_data = ti.xcom_pull(task_ids= 'data_extraction')
    df = pd.DataFrame(raw_data)
    df = df.iloc[:20,:]
    rec = df.to_records(index=False)
    data = list(rec)
    values_str = ', '.join(str(row) for row in data)
    ti.xcom_push(key='transformed_data',value=values_str)



default_args = {
    'owner': 'rohit',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


with DAG(
    dag_id='data_transformation_v1',
    default_args=default_args,
    start_date=datetime(2024,7,1),
    schedule_interval='@daily',
    catchup=False,
) as dag:
    
    data_extraction = HttpOperator(
                            task_id="data_extraction",
                            method="GET",
                            http_conn_id='http_connection',     # connection id of http connection
                            endpoint="newspapers.json",
                            headers={"Content-Type": "application/json"},
                            dag=dag,
                            response_filter= lambda response : json.loads(response.content).get('newspapers')
                    )
    

    table_creation = SqliteOperator(
        task_id='table_creation',
        sqlite_conn_id='db_connection',  # connection id of sqlite connection
        sql = '''
                CREATE TABLE IF NOT EXISTS newspaper_data (
                id INTEGER PRIMARY KEY,
                lccn TEXT,
                url TEXT,
                state TEXT,
                title TEXT
                );
            '''
    )

    transform_data = PythonOperator(
        task_id='transform_data',
        python_callable=data_transformation
    )
    
    data_insertion = SqliteOperator(
        task_id='data_insertion',
        sqlite_conn_id='db_connection',
        sql = '''
                INSERT INTO newspaper_data (lccn, url, state, title) VALUES  {{ ti.xcom_pull(key='transformed_data', task_ids='transform_data')}};
            '''
    )
    

    data_extraction >> [table_creation, transform_data] >> data_insertion