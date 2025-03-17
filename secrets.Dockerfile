FROM python:3.12-slim-bullseye

WORKDIR /app/script

RUN python -m pip install bitwarden-sdk

COPY secret.py /app/script/secret.py

ENV PATH="$PATH:/app/script"

CMD [ "/app/script/secret.py" ]