FROM python:3.15-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY scraper/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt
COPY scraper /app/scraper
CMD ["sh", "-c", "python -m scraper.collector --config scraper/examples/fixture-source.json --output /data/candidates.json && python -m scraper.history --db /data/prices.sqlite import --input /data/candidates.json"]
