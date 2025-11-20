FROM public.ecr.aws/lambda/python:3.11

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy application code
COPY app.py ${LAMBDA_TASK_ROOT}/
COPY prompt_examples/ ${LAMBDA_TASK_ROOT}/prompt_examples/

# Set the CMD to your handler
CMD [ "app.handler" ]
