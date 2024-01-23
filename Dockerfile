FROM python:3.11

SHELL ["/bin/bash", "-c"]

WORKDIR ./NSE_chatbot

RUN pip install -r requirements.txt


CMD ["python", "main.py"]