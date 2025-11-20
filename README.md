# threads-connector-persona-ai

This project is a template for deploying a Lambda function that automatically generates Threads posts based on persona guides stored in S3 using OpenAI LLM, triggered by an EventBridge schedule every 5 hours. It uses Terraform to provision S3, Lambda, IAM, and EventBridge resources, and Docker to build the Lambda image.

## Components
- **Lambda**: Reads persona files from S3, generates posts using OpenAI, and sends them to the Threads API via API Gateway.
- **EventBridge**: Triggers Lambda on a `rate(5 hours)` schedule.
- **S3**: Stores persona instruction files (`chief.txt`, `stock_analyzer.txt`, etc.).
- **Secrets Manager**: Stores OpenAI API key and Threads API Gateway key.
- **IAM Role**: Includes permissions for Lambda execution logs, S3 read access, and Secrets Manager retrieval.

## Lambda Code
- Location: `lambda/app.py`
- Features:
  - Reads OpenAI and Threads API keys from Secrets Manager.
  - Retrieves persona files from S3 and combines them with the prompt template (`prompt_examples/threads_prompt_example.txt`).
  - Generates posts using OpenAI Chat Completions API and sends them to API Gateway (`THREADS_POST_URL`).
- Environment Variables:
  - `PERSONA_BUCKET`: Bucket name where persona files are stored
  - `PERSONA_KEYS`: Comma-separated list of persona files (e.g., `chief.txt,stock_analyzer.txt`)
  - `OPENAI_SECRET_NAME`: Secret name containing OpenAI key (JSON `{ "api_key": "..." }` or key string)
  - `THREADS_API_SECRET_NAME`: Secret name containing Threads API Gateway key
  - `THREADS_POST_URL`: API Gateway Invoke URL (default provided)
  - `THREADS_USER_ID`: User ID to pass to Threads API (default `default`)
  - `OPENAI_MODEL`: OpenAI model name to use (default `gpt-4o-mini`)

## Docker Image Build
Lambda is deployed as a container image. Build the image locally, push it to ECR, and pass the URI to the `lambda_image_uri` variable.

```bash
# Run from root directory
DOCKER_IMAGE=threads-persona-lambda:latest

docker build -f docker/lambda.Dockerfile -t ${DOCKER_IMAGE} .
# Tag and push to ECR, then set the URI as a terraform variable
```

## Terraform Deployment
The `terraform/` directory contains the configuration to deploy the required resources.

```bash
cd terraform
terraform init
terraform apply \
  -var="persona_bucket_name=<bucket-name>" \
  -var="lambda_image_uri=<ECR image URI>" \
  -var="openai_secret_name=<OpenAI secret name>" \
  -var="threads_api_secret_name=<API Gateway secret name>" \
  -var="persona_files=[\"chief.txt\",\"stock_analyzer.txt\"]"
```

Key Outputs:
- `persona_bucket_name`: Persona bucket name
- `lambda_function_arn`: Lambda ARN
- `eventbridge_rule_arn`: Scheduling Rule ARN

## Prompt Examples
`prompt_examples/threads_prompt_example.txt` is a template for inserting persona instructions into prompts. Upload persona files to the same bucket and pass the filenames to Lambda environment variables.

## API Gateway Sample Payload
Lambda sends POST requests to API Gateway in the following format:
```json
{
  "user_id": "default",
  "post_text": "Hello from the Threads API via API Gateway!"
}
```
