import pandas as pd
import json
from datetime import datetime
import pytz
# Set timezone
tz = pytz.timezone('Europe/Berlin')

def generate_sql_slack_message(data: str, file: str):
    # Generate the current timestamp
    current_timestamp = datetime.now(tz).strftime("%d-%m-%Y %H:%M:%S")
    
    # Generate summary 
    summary = data['summary']
    summary_json = f"📅 {current_timestamp} \n✅ *Successful tests:* {summary['success_tests']} \n❌ *Failed_ tests:* {summary['failed_tests']} \n📊 <{file}|Download Report>"
    
    # Generate table with column test status
    df = pd.DataFrame(data['tests'])[1:]
    df['column_name'] = df['parameters'].apply(lambda x: x['column_name'])
    column_status_json = f"```{df[['column_name','status']].to_markdown()}```"
    
    # Template
    slack_message_template = {
        "blocks": [
        	{
        		"type": "header",
        		"text": {
        			"type": "plain_text",
        			"text": "Drift Detection Report ❄️"
        		}
        	},
            {
        		"type": "section",
                "text": {
        			"type": "mrkdwn",
        			"text": summary_json
        		}
        	},
            {
        		"type": "section",
                "text": {
        			"type": "mrkdwn",
        			"text": column_status_json
        		}
        	}
        ]
    }
    slack_message = json.dumps(slack_message_template).replace('\\n','\\\\n').replace('\\u','\\\\u')
    sql = f"""CALL SYSTEM$SEND_SNOWFLAKE_NOTIFICATION(
                SNOWFLAKE.NOTIFICATION.APPLICATION_JSON('{slack_message}'),
                SNOWFLAKE.NOTIFICATION.INTEGRATION('my_slack_webhook_int'))"""
    return sql

def generate_sql_email_message(data: str, file: str):
    # Generate the current timestamp
    current_timestamp = datetime.now(tz).strftime("%d-%m-%Y %H:%M:%S")
   
   # Generate summary 
    summary = data['summary']

    # Generate table with column test status
    df = pd.DataFrame(data['tests'])[1:]
    df['column_name'] = df['parameters'].apply(lambda x: x['column_name'])
    df = df[['column_name','status']]
    
    email_content = f"""
    📅 {current_timestamp} <br>
    ✅ Successful tests: {summary['success_tests']} <br>
    ❌ Failed_ tests: {summary['failed_tests']} <br>
    📊 <a href="{file}">Download Report</a>
    
    <p>{df.to_html().replace("'",'"')}</p>
    """
    
    sql = f"""CALL SYSTEM$SEND_SNOWFLAKE_NOTIFICATION(
                SNOWFLAKE.NOTIFICATION.TEXT_HTML('{email_content}'),
                SNOWFLAKE.NOTIFICATION.EMAIL_INTEGRATION_CONFIG('my_email_int','Drift Detection Report ❄️ {current_timestamp}',ARRAY_CONSTRUCT('michael.gorkow@snowflake.com')))"""
    return sql
