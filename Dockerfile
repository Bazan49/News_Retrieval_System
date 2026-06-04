FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --index-url https://download.pytorch.org/whl/cpu torch==2.10.0+cpu

RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu --retries 10 --timeout 120 --resume-retries 5 -r requirements.txt \
    && python -m nltk.downloader punkt_tab

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
