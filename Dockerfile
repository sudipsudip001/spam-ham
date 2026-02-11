FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Download required NLTK data
RUN python -m nltk.downloader -d ${LAMBDA_TASK_ROOT}/nltk_data stopwords punkt

# Copy app + models
COPY . .

ENV NLTK_DATA=${LAMBDA_TASK_ROOT}/nltk_data

CMD ["main.handler"]
