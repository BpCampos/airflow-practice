from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.macros import ds_add
import pendulum
import os
from os.path import join
import pandas as pd

with DAG(
        "dados_climaticos",
        start_date=pendulum.datetime(2024, 5, 24, tz="UTC"),
        schedule_interval='0 0 * * 1', # executar toda segunda feira
) as dag:

    task1 = BashOperator(
            task_id = 'cria_pasta',
            bash_command = 'mkdir -p "/home/bpcampos/Ubuntu/airflow-test/semana={{data_interval_end.strftime("%Y-%m-%d")}}"'
            )

    def extrai_dados(data_interval_end):
        city = 'Boston'
        key = '9WNZKK3DYNWU428ZDT4VVU64K'
        
        URL = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{data_interval_end}/{ds_add(data_interval_end, 7)}?key={key}&unitGroup=metric&include=days&key={key}&contentType=csv'
        
        df = pd.read_csv(URL)
        
        file_path = f'/home/bpcampos/Ubuntu/airflow-test/semana={data_interval_end}/'
        
        df.to_csv(file_path + 'dados_brutos.csv')
        df[['datetime', 'tempmin', 'temp', 'tempmax']].to_csv(file_path + 'temperaturas.csv')
        df[['datetime', 'description', 'icon']].to_csv(file_path + 'condicoes.csv')

    task2 = PythonOperator(
        task_id = 'extrai_dados',
        python_callable = extrai_dados,
        op_kwargs = {'data_interval_end': '{{data_interval_end.strftime("%Y-%m-%d")}}'}
    )

    task1 >> task2