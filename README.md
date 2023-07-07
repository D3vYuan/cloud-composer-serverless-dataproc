<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<div id="top"></div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h2 align="center">Serverless Dataproc Data Pipeline</h2>
  <p align="center">
    Case Study - Orchestrating Serverless Dataproc with Cloud Composer
  </p>
  <!--div>
    <img src="images/profile_pic.png" alt="Logo" width="80" height="80">
  </div-->
</div>

---

<!-- TABLE OF CONTENTS -->

## Table of Contents

<!-- <details> -->
<ol>
    <li>
        <a href="#about-the-project">About The Project</a>
    </li>
    <li>
        <a href="#current-operation">Current Operation</a>
        <ul>
            <li><a href="#via-cloud-console">Via Cloud Console</a></li>
        </ul>
    </li>
    <li>
        <a href="#setup">Setup</a>
        <ul>
            <li><a href="#cloud-storage">Cloud Storage</a></li>
            <li><a href="#bigquery">BigQuery</a></li>
            <li><a href="#iam">IAM</a></li>
            <li><a href="#cloud-composer">Cloud Composer</a></li>
        </ul>
    </li>
    <li>
        <a href="#implementation">Implementation</a>
        <ul>
            <li><a href="#run-serverless-batch">Run Serverless Batch</a></li>
        </ul>
    </li>
    <li><a href="#usage">Usage</a>
        <ul>
            <li><a href="#via-cloud-composer">Via Cloud Composer</a></li>
        </ul>
    </li>
    <li><a href="#challenges">Challenges</a></li>
    <li><a href="#possible-enhancements">Possible Enhancements</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
</ol>
<!-- </details> -->

---

<!-- ABOUT THE PROJECT -->

## About The Project

This project is created to showcase how we can leverage `Cloud Composer` to trigger the `Serverless Dataproc` batch job to run a `Java` application which will extract data from `BigQuery` and perform decryption and re-encryption on it before saving it back to `BigQuery`

The following are some of the requirements:

- Orchestrate the execution of `Java` application over `Serverless Dataproc` using `Cloud Composer`

`NOTE:` This repository is the continuation of the previous serverless dataproc [repository][ref-serverless-dataproc]

<p align="right">(<a href="#top">back to top</a>)</p>

---

<!-- Current Operation -->

## Current Operation

Base on the requirements, the following is the current operation:
- `Cloud Console` - The current execution of the `Serverless Dataproc` is through the configuration in the `Cloud Console`

<p align="right">(<a href="#top">back to top</a>)</p>

### Via Cloud Console

The following shows the configuration for the `Serverless Dataproc` batch job:
- `Main Class`: com.example.services.Application
- `Jar Files`: \<Your-Bucket-Application\>
- `Arguments`: 
    - *dataset-id*: \<Your-Project-Id\> 
    - *project_id*: \<Your-Dataset-Name\>
    - *source-table*: users
    - *destination-table*: users_temp
    - *bigquery-location*: us-central1
    - *google-cloud-bucket*: gs://encryption-poc/
    - *read-limit-rows*: \<Number-of-rows-to-processed\>
- Leave the rest as default (or blanks)
<br/>

|![dataproc-serverless-configuration-a][dataproc-serverless-configuration-a]|
|:--:| 

|![dataproc-serverless-configuration-b][dataproc-serverless-configuration-b] |
|:--:| 
| *Configuration for Serverless Dataproc* |

<br/>

<p align="right">(<a href="#top">back to top</a>)</p>

---

<!-- Setup -->

<div id="cloud-composer-setup"></div>

## Setup

Base on the requirements, the following components are required to be setup:

- `Cloud Storage` - Temporarily house the data to be sent to `Bigquery`
- `BigQuery` - Warehouse storage to save the data from the `Looker API` for audit and analytics purposes
- `IAM` - Provide the sufficient permissions to the `Cloud Composer` service account to access `Cloud Storage` and `BigQuery`
- `Cloud Composer` - Orchestrate the data flow to start the `Serverless Dataproc`

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="cloud-storage-setup"></div>

### Cloud Storage

Create a `Cloud Storage` bucket (E.g. `encryption_poc`) to house the following:
- `Application Binary` - The java application jar to be executed
- `Dataproc Logs Folder` - The folder to store the temporary logs for `Serverless Dataproc`



#### Application Binary

Upload the `Java` application binary into the `Cloud Storage` created <a href="#top">above</a>

|![cloud-storage-with-java-application][cloud-storage-with-java-application] |
|:--:| 
| *Upload Java Application into bucket* |

<br/>

<p align="right">(<a href="#top">back to top</a>)</p>

#### Dataproc Logs Folder

Create a temporary folder (E.g. `temp`) to house the logs for `Serverless Dataproc` job

|![cloud-storage-with-temp-folder][cloud-storage-with-temp-folder] |
|:--:| 
| *Temporary folder for Dataproc Logs* |

<br/>

<p align="right">(<a href="#cloud-storage-setup">back to top</a>)</p>

### BigQuery

Create a new `dataset` containing the following tables:
- `users` - Table containing the *encrypted* and *decrypted* data
- `users_temp` - Table that is used to temporary store the *processed* data from `Serverless Dataproc`

<br/>

<p align="right">(<a href="#top">back to top</a>)</p>

#### users

This following will be the schema for the `user` table, this table will be use to store the encrypted and decrypted text <br/>

|#|Field Name|Description|Type|Mode|
|--|--|--|--|--|
|1|id|An identifier to differentiate the row for updating of the row subsequently|Integer|Required|
|2|cipher_text|The encrypted text provided by the customer|Integer|Required|
|3|dek|The encrypted key to decrypt the customer provided text|Integer|Required|
|4|decrypted_email|The plaintext of the customer provided text|Integer|Required|
|5|bq_encryption_key|The encrypted key to decrypted the bq encrypted text|Integer|Required|
|6|bq_encrypted_email|The encrypted text using bq compliant algorithm|Integer|Required|

<br/>

<p align="right">(<a href="#top">back to top</a>)</p>

#### users_Temp

This following will be the schema for the `user_temp` table, this table will be use to temporary store the decrypted data before updating it back to `user` table. The join will be done based on the *id* field
<br/>

|#|Field Name|Description|Type|Mode|
|--|--|--|--|--|
|1|id|An identifier to differentiate the row for updating of the row subsequently|Integer|Required|
|2|cipher_text|The encrypted text provided by the customer|Integer|Required|
|3|dek|The encrypted key to decrypt the customer provided text|Integer|Required|
|4|decrypted_email|The plaintext of the customer provided text|Integer|Required|
|5|bq_encryption_key|The encrypted key to decrypted the bq encrypted text|Integer|Required|
|6|bq_encrypted_email|The encrypted text using bq compliant algorithm|Integer|Required|

<br/>

<p align="right">(<a href="#top">back to top</a>)</p>

### IAM

Assign the sufficient permissions for the `Cloud Composer` service account to access `Cloud Storage` and `BigQuery` during the dag run.

| ![cloud-composer-hosted-sa][cloud-composer-hosted-sa] | 
|:--:| 
| *Cloud Composer Service Account* |

<br>

`NOTE:` While the following image shows the service account being assigned *admin* rights, one may just provide sufficient permissions to the account for accessing `Cloud Storage` and `BigQuery` <br/>

| ![cloud-composer-hosted-sa-permissions][cloud-composer-hosted-sa-permissions] | 
|:--:| 
| *Cloud Composer Service Account Privileges* |

<p align="right">(<a href="#top">back to top</a>)</p>

### Cloud Composer

#### Setup Variables

The following are the *variables* needed for the dag run:

|#|Variables|Description|Example
|--|--|--|--|
|1|`dataproc_bigquery_jar_file`|The java class to run on Dataproc|gs://encryption-poc/kms-utils-1.1.jar
|2|`dataproc_bigquery_jar_main_class`|Main class to execute on Dataproc|com.example.services.Application
|3|`dataproc_bigquery_project_id`|Project ID for the BigQuery related to the Dataproc|
|4|`dataproc_bucket_name`|Temporary storage for Dataproc logs|gs://encryption-poc/temp
|5|`dataproc_bigquery_location`|Location of the BigQuery related to the Dataproc|us-central1
|6|`dataproc_bigquery_dataset_id`|Dataset of the BigQuery related to the Dataproc|encryption_poc
|7|`dataproc_bigquery_source_table`|Encrypted Data related to the Dataproc|users
|8|`dataproc_bigquery_destination_table`|Temporary storage for processed data from Dataproc|users_temp
|9|`dataproc_bigquery_read_limits`|Number of rows to processed for each Dataproc execution|2
|10|`dataproc_bigquery_service_account`|Service Account to execute the Dataproc Job|xxxxxxxxxxxx-compute@developer.gserviceaccount.com
|11|`dataproc_bigquery_subnet`|Subnet to run the Dataproc Job|
|12|`dataproc_runtime_version`|Runtime version for Dataproc|2.1 <br/> `NOTE:` Please refer [here][ref-serverless-dataproc-runtime] for latest runtime information

<br/>

<p align="right">(<a href="#top">back to top</a>)</p>

#### Upload Dags
Upload dag file *trigger-serverless-batch.py* into the `Cloud Composer` dag bucket <br/>

| ![cloud-composer-hosted-dag-files][cloud-composer-hosted-dag-files] | 
|:--:| 
| *Cloud Composer Dag Files* |

Verify that the *trigger-serverless-batch-dataproc* dag appears in `Cloud Composer` 

| ![cloud-composer-hosted-dag][cloud-composer-hosted-dag] | 
|:--:| 
| *Cloud Composer Dag* |    

<br/>

<p align="right">(<a href="#top">back to top</a>)</p>

---

## Implementation

<br/>

| ![cloud-composer-hosted-dag][cloud-composer-hosted-dag] | 
|:--:| 
| *Cloud Composer Data Pipeline* |

<br/>

Base on the requirements, the following are the tasks in the pipelines:

- `Run Serverless Batch` - Trigger to run the `Java` application with the `Serverless Dataproc` batch job 

<p align="right">(<a href="#top">back to top</a>)</p>

### Run Serverless Batch
This task make use of the `DataprocCreateBatchOperator` to create a `Serverless Dataproc` job and running the application specify in the *BATCH_CONFIG*

```python
BATCH_ARGUMENTS = [f"--project-id={PROJECT_ID}", 
                   f"--bigquery-location={BIGQUERY_LOCATION}",
                   f"--dataset-id={BIGQUERY_DATASET_ID}", 
                   f"--source-table={BIGQUERY_SOURCE_TABLE_NAME}",
                   f"--destination-table={BIGQUERY_DESTINATION_TABLE_NAME}",
                   f"--google-cloud-bucket={BUCKET_NAME}",
                   f"--read-limit-rows={BIGQUERY_READ_LIMITS}"]

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
            }
    }
}

run_serverless_batch = DataprocCreateBatchOperator(
    task_id="run_serverless_batch",
    project_id=PROJECT_ID,
    region=BIGQUERY_LOCATION,
    batch_id=str(uuid.uuid4()),
    batch=BATCH_CONFIG,
)
```
<br/>
<p align="right">(<a href="#top">back to top</a>)</p>

---

<!-- USAGE EXAMPLES -->

## Usage

There are 1 modes to test out the implementation
- Running via `Cloud Composer` - by uploading the *trigger-serverless-batch.py* into `Cloud Composer` dag folder and executing the corresponding dag

<p align="right">(<a href="#top">back to top</a>)</p>

### Via Cloud Composer
`NOTE:` Assuming that the `Cloud Composer` setup steps have been completed, otherwise see <a href="#cloud-composer-setup">here</a> before proceeding. <br/>

The following are the execution steps to run the code in `Cloud Composer`:

- Click the *trigger-serverless-batch-dataproc* to enter the dag details <br/>
    **Dag** <br/>
    | ![cloud-composer-hosted-dag][cloud-composer-hosted-dag] | 
    |:--:| 
    | *Cloud Composer Dag* |

- Click the play button to execute *trigger-serverless-batch-dataproc* and wait for it to be completed <br/>
    **Dag** <br/>

    | ![cloud-composer-hosted-dag-run][cloud-composer-hosted-dag-run] | 
    |:--:| 
    | *Cloud Composer Run Dag* |

- Verify that the program executed successfully and generated the output file <br/>
    **Log** <br/>

    | ![cloud-composer-hosted-dag-log][cloud-composer-hosted-dag-log] | 
    |:--:| 
    | *Cloud Composer Run Log* |

- Verify that the program has spinned off a `Serverless Dataproc` job<br/>
    **Serverless Dataproc** <br/>
    
    | ![cloud-composer-hosted-dataproc-output][cloud-composer-hosted-dataproc-output] | 
    |:--:| 
    | *Serverless Dataproc Output* |

- Verify that the program executed successfully and inserted the data into `BigQuery` <br/>
    **BigQuery** <br/>

    | ![cloud-composer-hosted-bq-output][cloud-composer-hosted-bq-output] | 
    |:--:| 
    | *BigQuery Output* |

<p align="right">(<a href="#top">back to top</a>)</p>

---

<!-- Challenges -->
## Challenges

The following are some challenges encountered:
- Specifying *runtime* for `Serverless Dataproc`
<p align="right">(<a href="#top">back to top</a>)</p>

### Challenge #1: Specifying Runtime for `Serverless Dataproc`
<br/>

**Observations** <br/>

Originally without specifying the *runtime*, the run results were inconsistent, with runs failing from time to time. The suspect could be due to the environment that are always changing in each run, and that it may not have the necessary libraries to run the application.

<br/>

**Resolution** <br/>

Specify the *runtime* in the *BATCH_CONFIG* so that the environment is fixed to a particular version, that helps in making the runs yielding more consistent results.

```
BATCH_CONFIG = {
    ...
    "runtime_config": {
        "version": DATAPROC_RUNTIME_VERSION
    },
    ...
}
```

<br/>

<p align="right">(<a href="#top">back to top</a>)</p>

---

<!-- Enhancements -->
## Possible Enhancements

- [ ] Split the Java codes to just performing the *encryption* and *decryption* functions, and let the `Cloud Composer` handles the fetching and updating of the data into `BigQuery`

<!-- See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues). -->

<p align="right">(<a href="#top">back to top</a>)</p>

## Acknowledgments

- [Serverless Dataproc Repository (Private)][ref-serverless-dataproc]
- [Readme Template][template-resource]

<p align="right">(<a href="#top">back to top</a>)</p>

---

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[template-resource]: https://github.com/othneildrew/Best-README-Template/blob/master/README.md
[ref-serverless-dataproc]: https://github.com/D3vYuan/serverless-dataproc-bigquery
[ref-serverless-dataproc-runtime]: https://cloud.google.com/dataproc-serverless/docs/concepts/versions/spark-runtime-versions

[dataproc-serverless-configuration-a]: ./images/dataproc-serverless-configuration-a.png
[dataproc-serverless-configuration-b]: ./images/dataproc-serverless-configuration-b.png

[cloud-storage-with-java-application]: ./images/cloud-storage-with-java-application.png
[cloud-storage-with-temp-folder]: ./images/cloud-storage-with-temp-folder.png

[cloud-composer-hosted-sa]: ./images/cloud-composer-hosted-service-account.png
[cloud-composer-hosted-sa-permissions]: ./images/cloud-composer-hosted-service-account-permissions.png

[cloud-composer-hosted-dag-files]: ./images/cloud-composer-hosted-dag-files.png
[cloud-composer-hosted-dag]: ./images/cloud-composer-hosted-dag.png
[cloud-composer-hosted-dag-run]: ./images/cloud-composer-hosted-dag-run.png
[cloud-composer-hosted-dag-log]: ./images/cloud-composer-hosted-dag-log.png
[cloud-composer-hosted-dag-output]: ./images/cloud-composer-hosted-dag-output.png
[cloud-composer-hosted-dataproc-output]: ./images/cloud-composer-hosted-dataproc-output.png
[cloud-composer-hosted-bq-output]: ./images/cloud-composer-hosted-bq-output.png


