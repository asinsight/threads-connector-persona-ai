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


def post_to_threads_api(post_url: str, api_key: str, user_id: str, post_text: str, topic_tag: str) -> None:
    payload = {"user_id": user_id, "post_text": post_text, "topic_tag": topic_tag}
    LOGGER.info(f"Payload: {payload}")
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    LOGGER.info(f"Posting to Threads API: {payload}")
    response = requests.post(post_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    LOGGER.info(f"Successfully posted to Threads API. Status code: {response.status_code}")


def handler(event, context):  # pylint: disable=unused-argument
    persona_bucket = os.environ.get("PERSONA_BUCKET")
    persona_keys = os.environ.get("PERSONA_KEYS", "chief.txt,stock_analyzer.txt").split(",")
    post_url = os.environ.get("THREADS_POST_URL", "https://aylhkweg4d.execute-api.us-east-1.amazonaws.com/dev/post")
    user_id = os.environ.get("THREADS_USER_ID", "default")
    model = os.environ.get("OPENAI_MODEL", "gpt-5.1")

    if not persona_bucket or not post_url:
        raise ValueError("PERSONA_BUCKET and THREADS_POST_URL environment variables are required")

    openai_secret_name = os.environ.get("OPENAI_SECRET_NAME", "openai-key")
    api_secret_name = os.environ.get("THREADS_API_SECRET_NAME", "threads-api-key")

    openai_secret = get_secret(openai_secret_name, "api_key")
    api_secret = get_secret(api_secret_name, "api_key")

    openai_client = OpenAI(api_key=openai_secret.get("api_key"))
    prompt_template = load_prompt_example()

    # Randomly select one persona key
    persona_keys_cleaned = [key.strip() for key in persona_keys if key.strip()]
    if not persona_keys_cleaned:
        raise ValueError("No valid persona keys found")

    selected_persona_key = random.choice(persona_keys_cleaned)
    LOGGER.info(f"Randomly selected persona: {selected_persona_key}")
    topic_tag_mapping = {
        "chief.txt": "집밥 요리",
        "stock_analyzer.txt": "미국 주식"
    }
    topic_tag = topic_tag_mapping.get(selected_persona_key, "일상")

    # Process only the selected persona
    persona_text = fetch_persona(persona_bucket, selected_persona_key)
    prompt = build_prompt(persona_text, prompt_template)
    post_text = generate_post(model, openai_client, prompt)
    post_to_threads_api(post_url, api_secret.get("api_key"), user_id, post_text, topic_tag)

    return {
        "status": "success",
        "posts_created": 1,
        "persona_used": selected_persona_key,
        "post_text": post_text,
        "topic_tag": topic_tag
    }
