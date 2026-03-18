import os
import json
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIStatusError

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("gateway.log"), logging.StreamHandler()]
)


class GroqGateway:
    def __init__(self, cache_file="cache.json", log_file="analytics.jsonl"):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment.")

        self.client = Groq(api_key=api_key)
        self.cache_file = cache_file
        self.log_file = log_file
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=4)

    def _log_analytics(self, event):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def request(self, prompt, model="llama-3.1-8b-instant", temperature=0.7, max_tokens=512):
        # Cache check
        cache_key = f"{model}_{prompt}_{temperature}"
        if cache_key in self.cache:
            logging.info(f"Cache hit: {model}")
            return self.cache[cache_key]

        start_time = time.time()
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                duration = time.time() - start_time
                content = response.choices[0].message.content
                usage = response.usage

                # Performance tracking
                analytics_data = {
                    "timestamp": datetime.now().isoformat(),
                    "model": model,
                    "duration_sec": round(duration, 3),
                    "tokens": usage.total_tokens,
                    "status": "success"
                }
                self._log_analytics(analytics_data)

                # Update local storage
                self.cache[cache_key] = content
                self._save_cache()

                return content

            except RateLimitError:
                # Exponential backoff
                wait = 2 ** attempt
                logging.warning(f"Rate limit. Retrying in {wait}s...")
                time.sleep(wait)
            except (APIStatusError, Exception) as e:
                logging.error(f"Request failed: {e}")
                break

        return "Error: Request failed."

    def run_benchmark(self, prompt, models=None):
        if models is None:
            models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]

        print(f"\n{'=' * 15} Benchmark {'=' * 15}")
        for model in models:
            start = time.time()
            self.request(prompt, model=model)
            print(f"Model: {model:<25} | Time: {time.time() - start:.4f}s")
        print(f"{'=' * 41}\n")


if __name__ == "__main__":
    gateway = GroqGateway()

    # Example usage
    print("Testing standard request...")
    print(f"Result: {gateway.request('What is Python in 10 words?')}")

    # Performance test
    gateway.run_benchmark("Explain AI latency.")