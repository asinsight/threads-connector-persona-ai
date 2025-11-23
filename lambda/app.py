import json
import os
from typing import Dict
import time
import boto3
import requests
from openai import OpenAI
import logging
import random
from botocore.exceptions import ClientError

# Configure logging
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


s3_client = boto3.client("s3")
secrets_client = boto3.client("secretsmanager")

def get_secret(secret_name: str, key_name: str) -> Dict[str, str]:
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret_string = response.get("SecretString", "{}")
    try:
        return json.loads(secret_string)
    except json.JSONDecodeError:
        return {key_name: secret_string}


def load_prompt_example() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "prompt_examples", "threads_prompt_example.txt")
    with open(prompt_path, "r", encoding="utf-8") as prompt_file:
        return prompt_file.read()


def fetch_persona(bucket: str, key: str) -> str:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read().decode("utf-8")


def build_prompt(persona_text: str, prompt_template: str) -> str:
    return prompt_template.format(persona_content=persona_text)


def generate_post(model: str, client: OpenAI, prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=500,
        )
        LOGGER.info(f"Completion choices: {completion.choices}")
        LOGGER.info(f"Finish reason: {completion.choices[0].finish_reason}")
        LOGGER.info(f"Post generated successfully. Finish reason: {completion.choices[0].finish_reason}")
        return completion.choices[0].message.content
    except Exception as e:
        LOGGER.error(f"Error generating post: {str(e)}", exc_info=True)
        raise


def invoke_threads_lambda(function_name: str, user_id: str, post_text: str, topic_tag: str) -> None:
    payload = {"user_id": user_id, "post_text": post_text, "topic_tag": topic_tag}
    # Wrap payload to mimic API Gateway event
    event_payload = {"body": json.dumps(payload)}
    LOGGER.info(f"Invoking Lambda {function_name} with payload: {event_payload}")
    
    lambda_client = boto3.client("lambda")
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(event_payload)
        )
        
        response_payload = json.loads(response["Payload"].read())
        LOGGER.info(f"Lambda invocation response: {response_payload}")
        
        if response.get("FunctionError"):
             LOGGER.error(f"Lambda invocation failed with error: {response_payload}")
             raise Exception(f"Lambda invocation failed: {response_payload}")

    except ClientError as e:
        LOGGER.error(f"Error invoking Lambda: {e}")
        raise

def handler(event, context):  # pylint: disable=unused-argument
    persona_bucket = os.environ.get("PERSONA_BUCKET")
    persona_keys = os.environ.get("PERSONA_KEYS", "chief.txt,stock_analyzer.txt").split(",")
    target_function_name = os.environ.get("THREADS_CONNECTOR_FUNCTION_NAME", "threads-connector-dev-api")
    user_id = os.environ.get("THREADS_USER_ID", "default")
    model = os.environ.get("OPENAI_MODEL", "gpt-5.1")

    if not persona_bucket or not target_function_name:
        raise ValueError("PERSONA_BUCKET and THREADS_CONNECTOR_FUNCTION_NAME environment variables are required")

    openai_secret_name = os.environ.get("OPENAI_SECRET_NAME", "openai-key")

    openai_secret = get_secret(openai_secret_name, "api_key")

    openai_client = OpenAI(api_key=openai_secret.get("api_key"))
    prompt_template = load_prompt_example()

    # Randomly select one persona key
    persona_keys_cleaned = [key.strip() for key in persona_keys if key.strip()]
    if not persona_keys_cleaned:
        raise ValueError("No valid persona keys found")

    selected_persona_key = random.choice(persona_keys_cleaned)
    LOGGER.info(f"Randomly selected persona: {selected_persona_key}")
    topic_tag_mapping = {
        "edu_mom.txt": "미국 교육",
        "chief.txt": "집밥 요리",
        "stock_analyzer.txt": "미국 주식"
    }
    topic_tag = topic_tag_mapping.get(selected_persona_key, "일상")

    # Process only the selected persona
    persona_text = fetch_persona(persona_bucket, selected_persona_key)
    prompt = build_prompt(persona_text, prompt_template)
    post_text = generate_post(model, openai_client, prompt)
    invoke_threads_lambda(target_function_name, user_id, post_text, topic_tag)

    return {
        "status": "success",
        "posts_created": 1,
        "persona_used": selected_persona_key,
        "post_text": post_text,
        "topic_tag": topic_tag
    }
