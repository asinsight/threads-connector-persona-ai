# threads-connector-persona-ai

이 프로젝트는 OpenAI LLM을 사용해 S3에 저장된 페르소나 가이드를 기반으로 Threads 게시물을 자동 생성하고, 5시간마다 EventBridge 스케줄로 실행되는 Lambda를 배포하기 위한 템플릿입니다. Terraform으로 S3, Lambda, IAM, EventBridge 리소스를 구성하고 Docker로 Lambda 이미지를 빌드합니다.

## 구성 요소
- **Lambda**: S3에서 페르소나 파일을 읽어 OpenAI로 게시물을 생성하고 API Gateway를 통해 Threads API에 전달합니다.
- **EventBridge**: `rate(5 hours)` 스케줄로 Lambda를 트리거합니다.
- **S3**: 페르소나 지침 파일(`chief.txt`, `stock_analyzer.txt` 등)을 저장합니다.
- **Secrets Manager**: OpenAI API 키와 Threads API Gateway 키를 저장합니다.
- **IAM Role**: Lambda 실행을 위한 로그, S3 읽기, Secrets Manager 조회 권한을 포함합니다.

## Lambda 코드
- 위치: `lambda/app.py`
- 기능:
  - Secrets Manager에서 OpenAI 및 Threads API 키를 읽습니다.
  - S3에서 페르소나 파일 목록을 가져와 프롬프트 템플릿(`prompt_examples/threads_prompt_example.txt`)과 결합합니다.
  - OpenAI Chat Completions API로 게시물을 생성하고, API Gateway(`THREADS_POST_URL`)로 전송합니다.
- 환경 변수:
  - `PERSONA_BUCKET`: 페르소나 파일이 저장된 버킷 이름
  - `PERSONA_KEYS`: 콤마 구분 페르소나 파일 목록 (예: `chief.txt,stock_analyzer.txt`)
  - `OPENAI_SECRET_NAME`: OpenAI 키가 저장된 Secret 이름 (JSON `{ "api_key": "..." }` 또는 키 문자열)
  - `THREADS_API_SECRET_NAME`: Threads API Gateway 키가 저장된 Secret 이름
  - `THREADS_POST_URL`: API Gateway Invoke URL (기본값 제공)
  - `THREADS_USER_ID`: Threads API에 전달할 사용자 ID (기본 `default`)
  - `OPENAI_MODEL`: 사용할 OpenAI 모델 이름 (기본 `gpt-4o-mini`)

## Docker 이미지 빌드
Lambda는 컨테이너 이미지로 배포됩니다. 로컬에서 이미지를 빌드하고 ECR에 푸시한 후 `lambda_image_uri` 변수에 전달하세요.

```bash
# 루트에서 실행
DOCKER_IMAGE=threads-persona-lambda:latest

docker build -f docker/lambda.Dockerfile -t ${DOCKER_IMAGE} .
# ECR에 태그 및 푸시 후 URI를 terraform 변수로 설정
```

## Terraform 배포
`terraform/` 디렉터리에는 필요한 리소스를 배포하기 위한 구성이 있습니다.

```bash
cd terraform
terraform init
terraform apply \
  -var="persona_bucket_name=<버킷이름>" \
  -var="lambda_image_uri=<ECR 이미지 URI>" \
  -var="openai_secret_name=<OpenAI secret 이름>" \
  -var="threads_api_secret_name=<API Gateway secret 이름>" \
  -var="persona_files=[\"chief.txt\",\"stock_analyzer.txt\"]"
```

주요 출력 값:
- `persona_bucket_name`: 페르소나 버킷 이름
- `lambda_function_arn`: Lambda ARN
- `eventbridge_rule_arn`: 스케줄링 Rule ARN

## 프롬프트 예제
`prompt_examples/threads_prompt_example.txt`는 페르소나 지시사항을 프롬프트에 삽입하기 위한 템플릿입니다. 페르소나 파일을 같은 버킷에 업로드한 후 Lambda 환경 변수에 파일명을 전달하세요.

## API Gateway 샘플 페이로드
Lambda는 다음 형식으로 API Gateway에 POST 요청을 보냅니다.
```json
{
  "user_id": "default",
  "post_text": "Hello from the Threads API via API Gateway!"
}
```
