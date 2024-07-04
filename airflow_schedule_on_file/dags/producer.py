from airflow import DAG, Dataset
from datetime import datetime
from airflow.decorators import task

data_set = Dataset('/home/ongraph/Desktop/airflow/airflow_schedule_on_file/test.txt')


with DAG(
    dag_id='producer_v1',
    schedule_interval= '@daily',
    start_date=datetime(2024,7,2),
    # catchup=False,
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
    }
) as dag:
    
    @task(outlets=[data_set])
    def producer_task():
        # This is producer which will produce data 
        with open(data_set.uri, 'a+') as f:
            f.write('producer_task')

    producer_task()