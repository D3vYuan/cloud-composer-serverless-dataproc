from datetime import datetime as dt
from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from datetime import datetime, timedelta 
import uuid

dag_owner = 'airflow'

default_args = {'owner': dag_owner,
        'start_date': dt.now() - timedelta(days=1),
        'depends_on_past': False,
        'retries': 3,
        'email_on_failure': False,
        'email_on_retry': False,
        'catchup': False,
        'retry_delay': timedelta(seconds=30),
        }

DATAPROC_RUNTIME_VERSION = Variable.get("dataproc_runtime_version")

DATAPROC_JAR_FILE = Variable.get("dataproc_bigquery_jar_file")
DATAPROC_MAIN_CLASS = Variable.get("dataproc_bigquery_jar_main_class")
DATAPROC_BIGQUERY_DEPENDENCIES = Variable.get("dataproc_bigquery_dependencies")

DATAPROC_SERVICE_ACCOUNT = Variable.get("dataproc_bigquery_service_account")
DATAPROC_SUBNET = Variable.get("dataproc_bigquery_subnet")

PROJECT_ID = Variable.get("dataproc_bigquery_project_id")
BUCKET_NAME = Variable.get("dataproc_bucket_name")

BIGQUERY_LOCATION = Variable.get("dataproc_bigquery_location")
BIGQUERY_DATASET_ID = Variable.get("dataproc_bigquery_dataset_id")

BIGQUERY_SOURCE_TABLE_NAME = Variable.get("dataproc_bigquery_source_table")
BIGQUERY_DESTINATION_TABLE_NAME = Variable.get("dataproc_bigquery_destination_table")

BIGQUERY_READ_LIMITS = Variable.get("dataproc_bigquery_read_limits")

BATCH_ARGUMENTS = [f"--project-id={PROJECT_ID}", 
                   f"--bigquery-location={BIGQUERY_LOCATION}",
                   f"--dataset-id={BIGQUERY_DATASET_ID}", 
                   f"--source-table={BIGQUERY_SOURCE_TABLE_NAME}",
                   f"--destination-table={BIGQUERY_DESTINATION_TABLE_NAME}",
                   f"--google-cloud-bucket={BUCKET_NAME}",
                   f"--read-limit-rows={BIGQUERY_READ_LIMITS}"]

# https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/dataproc.html#:~:text=tests/system/providers/google/cloud/dataproc/example_dataproc_spark.py
BATCH_CONFIG = {
    "spark_batch": {
        "jar_file_uris": [
            DATAPROC_JAR_FILE,
        ],
        "main_class": DATAPROC_MAIN_CLASS,
        "args": BATCH_ARGUMENTS
    },
    "runtime_config": {
        "version": DATAPROC_RUNTIME_VERSION
    },
    "environment_config":{
        "execution_config":{
            "service_account": DATAPROC_SERVICE_ACCOUNT,
            "subnetwork_uri": DATAPROC_SUBNET
            },
#         "peripherals_config": {
#             "spark_history_server_config": {
#                 "dataproc_cluster": f"projects/{project_id}/regions/{region}/clusters/{phs_server}"
#                 }
#             },
    }
}

with DAG(dag_id='trigger-serverless-batch-dataproc',
        default_args=default_args,
        description='Data pipeline to decrypt and encrypt information for BigQuery',
        schedule_interval='@daily',
        tags=['bigquery', 'dataproc']
):
    start = EmptyOperator(task_id='start')

    print(f"Processing: Batch Configuration - {BATCH_CONFIG}")

    run_serverless_batch = DataprocCreateBatchOperator(
        task_id="run_serverless_batch",
        project_id=PROJECT_ID,
        region=BIGQUERY_LOCATION,
        batch_id=str(uuid.uuid4()),
        batch=BATCH_CONFIG,
    )

    end = EmptyOperator(task_id='end')

    start >> run_serverless_batch >> end