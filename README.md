# Machine Learning in Snowflake
This repo contains a very simple example for a classical machine learning problem.  
Given some customer data from a fictional Ecommerce Company, we want to predict the yearly spent amount.

## What you'll do
In this example, you'll perform the following steps:
1. Import required Libraries
2. Create or Retrieve a Snowflake Session
3. Setup your Snowflake environment (Database, Schema, Warehouse)
4. Create an artificial E-Commerce dataset 
5. Feature Engineering (Variable Imputation & Encoding)
6. Distributed Hyperparameter Tuning for an XGBoost Regression Model
7. Evaluate your trained Model
8. Register your Model in Snowflake's Model Registry and visualize the Lineage
9. Automate the full pipeline with Snowflake's Python API and Notification Integrations
10. Clean Up

## Requirements
* Snowflake Account
* ML Lineage Feature (currently in PrPr, needs to be requested)
* [Slack App with Secret](https://docs.snowflake.com/en/user-guide/notifications/webhook-notifications#example-1-creating-a-secret-for-a-slack-webhook) (only required if you want to send notifications to Slack)

## Get Started
Register for a free Snowflake Trial Account:
- [Free Snowflake Trial Account](https://signup.snowflake.com/)

> [!IMPORTANT]
> Some features like the Feature Store require Snowflake Enterprise Edition or higher. Availability of specific Cortex LLM models can be found [here](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions#availability).

Integrate this Github Repository with Snowflake by running the following SQL code in a Snowflake Worksheet:
```sql
USE ROLE ACCOUNTADMIN;

-- Create warehouses
CREATE WAREHOUSE IF NOT EXISTS TRAIN_WH WITH WAREHOUSE_SIZE='MEDIUM';
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH WITH WAREHOUSE_SIZE='X-SMALL';

-- Create a fresh Database
CREATE OR REPLACE DATABASE SIMPLE_ML_DB;
USE SCHEMA SIMPLE_ML_DB.PUBLIC;

-- Create the integration with Github
CREATE OR REPLACE API INTEGRATION GITHUB_INTEGRATION_SIMPLE_ML_DEMO
    api_provider = git_https_api
    api_allowed_prefixes = ('https://github.com/michaelgorkow/')
    enabled = true
    comment='Michaels repository containing all the awesome code.';

-- Create the integration with the Github repository
CREATE GIT REPOSITORY GITHUB_REPO_SIMPLE_ML_DEMO 
	ORIGIN = 'https://github.com/michaelgorkow/snowflake_simple_ml' 
	API_INTEGRATION = 'GITHUB_INTEGRATION_SIMPLE_ML_DEMO' 
	COMMENT = 'Michaels repository containing all the awesome code.';

-- Fetch most recent files from Github repository
ALTER GIT REPOSITORY GITHUB_REPO_SIMPLE_ML_DEMO FETCH;

-- Create demo notebook
CREATE OR REPLACE NOTEBOOK SIMPLE_ML_DB.PUBLIC.SIMPLE_ML_DEMO FROM '@SIMPLE_ML_DB.PUBLIC.GITHUB_REPO_SIMPLE_ML_DEMO/branches/main/' MAIN_FILE = 'demo_notebook.ipynb' QUERY_WAREHOUSE = compute_wh;
ALTER NOTEBOOK SIMPLE_ML_DB.PUBLIC.SIMPLE_ML_DEMO ADD LIVE VERSION FROM LAST;

-- Create Email Notification Integration
CREATE OR REPLACE NOTIFICATION INTEGRATION my_email_int
  TYPE=EMAIL
  ENABLED=TRUE;

-- Create Slack Notification Integration (Optional)
CREATE OR REPLACE SECRET my_slack_webhook_secret
  TYPE = GENERIC_STRING
  SECRET_STRING = 'T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'; -- replace with your secret

CREATE OR REPLACE NOTIFICATION INTEGRATION my_slack_webhook_int
  TYPE=WEBHOOK
  ENABLED=TRUE
  WEBHOOK_URL='https://hooks.slack.com/services/SNOWFLAKE_WEBHOOK_SECRET'
  WEBHOOK_SECRET=my_slack_webhook_secret
  WEBHOOK_HEADERS=('Content-Type'='application/json');
```

## Snowflake Features in this demo
* [Snowflake's Git Integration](https://docs.snowflake.com/en/developer-guide/git/git-overview)
* [Snowpark](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
* [Snowpark ML](https://docs.snowflake.com/en/developer-guide/snowpark-ml/overview)
* [Snowflake Feature Store](https://docs.snowflake.com/en/developer-guide/snowpark-ml/feature-store/overview)
* [Snowflake Model Registry](https://docs.snowflake.com/en/developer-guide/snowpark-ml/model-registry/overview)
* [Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
* [Snowflake Notifications](https://docs.snowflake.com/en/user-guide/notifications/about-notifications)

## API Documentation
* [Snowpark API](https://docs.snowflake.com/developer-guide/snowpark/reference/python/latest/snowpark/index)
* [Snowpark ML API](https://docs.snowflake.com/en/developer-guide/snowpark-ml/reference/latest/index)
* [Snowflake Feature Store API](https://docs.snowflake.com/en/developer-guide/snowpark-ml/reference/latest/feature_store)
* [Snowflake Model Registry API](https://docs.snowflake.com/en/developer-guide/snowpark-ml/reference/latest/registry)