FROM python:3.12-alpine

WORKDIR /app

COPY printer_cleaner ./printer_cleaner
COPY VERSION ./VERSION

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "printer_cleaner"]
