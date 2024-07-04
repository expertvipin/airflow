from airflow import DAG, Dataset
from datetime import datetime
from airflow.decorators import task

data_set = Dataset('/home/ongraph/Desktop/airflow/airflow_schedule_on_file/test.txt')

# This DAG is scheduled on file system, it runs if producer produces the file 
with DAG(
    dag_id='consumer_v1',
    schedule= [data_set],
    start_date=datetime(2024,7,2),
    # catchup=False,
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
    }
) as dag:
    @task   
    def consumer_task():
        with open(data_set.uri, 'a+') as f:
            f.read()

    consumer_task()