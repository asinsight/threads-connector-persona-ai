import json
import os
from typing import Dict, List

import boto3
import requests
from openai import OpenAI
import logging
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
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=400,
    )
    return completion.choices[0].message.content


def post_to_threads_api(post_url: str, api_key: str, user_id: str, post_text: str) -> None:
    payload = {"user_id": user_id, "post_text": post_text}
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    response = requests.post(post_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()


def handler(event, context):  # pylint: disable=unused-argument
    persona_bucket = os.environ.get("PERSONA_BUCKET")
    persona_keys = os.environ.get("PERSONA_KEYS", "stock_analyzer.txt").split(",")
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

    posts: List[str] = []
    for key in persona_keys:
        persona_key = key.strip()
        if not persona_key:
            continue
        persona_text = fetch_persona(persona_bucket, persona_key)
        prompt = build_prompt(persona_text, prompt_template)
        post_text = generate_post(model, openai_client, prompt)
        posts.append(post_text)
        post_to_threads_api(post_url, api_secret.get("api_key"), user_id, post_text)

    return {"status": "success", "posts_created": len(posts)}
