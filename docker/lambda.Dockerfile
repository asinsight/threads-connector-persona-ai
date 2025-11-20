FROM public.ecr.aws/lambda/python:3.11

WORKDIR /var/task

COPY lambda/requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY lambda/ ./

CMD ["app.handler"]
