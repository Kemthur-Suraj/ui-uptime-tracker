import yaml, os, time, uuid
from playwright.sync_api import sync_playwright
from auth_token_fetcher import get_token
from exporters.otel_metric_push import record
from exporters.log_shipper import log_failure, log_success

# Load config
with open("/app/config/endpoints.yaml") as f:
    cfg = yaml.safe_load(f)
env = os.getenv("ENV", "dev")
env_cfg = cfg["environments"][env]
OTEL = env_cfg["otel_collector_endpoint"]
endpoints = env_cfg["endpoints"]

# Failure cache
failure_counts = {ep["name"]: 0 for ep in endpoints}

def probe():
    run_id = str(uuid.uuid4())
    for ep in endpoints:
        name, url, sel = ep["name"], ep["url"], ep["success_selector"]
        tags = {"env": env, "app": name}
        headers = {}
        if "auth" in ep:
            token = get_token()
            headers["Authorization"] = f"Bearer {token}"
        try:
            start = time.time()
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(extra_http_headers=headers)
                page.goto(url, timeout=30000)
                page.wait_for_selector(sel, timeout=10000)
                rt = time.time() - start
                success = 1
                browser.close()
            record(name, success, rt, tags)
            log_success(name, url, rt, tags)
            failure_counts[name] = 0
        except Exception as e:
            failure_counts[name] += 1
            record(name, 0, 0.0, tags)
            if failure_counts[name] <= 3:
                log_failure(name, url, str(e), run_id, tags)

def main():
    interval = 300  # 5 minutes
    while True:
        probe()
        time.sleep(interval)

if __name__ == "__main__":
    main()
