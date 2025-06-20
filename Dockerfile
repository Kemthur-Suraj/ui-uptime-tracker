FROM python:3.10-slim

# Install Playwright browsers
RUN pip install --no-cache-dir playwright \
 && playwright install --with-deps chromium

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ config/
COPY exporters/ exporters/
COPY auth_token_fetcher.py playwright_runner.py ./

# Logs volume
RUN mkdir -p /app/logs
VOLUME ["/app/logs"]

ENV ENV=dev
ENV UI_LOG_PATH=/app/logs/ui_render.log

ENTRYPOINT ["python", "playwright_runner.py"]
