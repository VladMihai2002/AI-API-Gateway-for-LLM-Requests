# Groq Gateway (Python)

This project is a small Python application that acts as a simple gateway for interacting with the Groq API and large language models. The goal of the project is to simulate a lightweight middleware layer between an application and an AI model.

Instead of sending requests directly to the API, all prompts go through a gateway class that manages the interaction with the model. This allows the project to add extra functionality such as caching, logging, basic analytics, and retry logic for rate limits.

The gateway stores responses in a local cache so that repeated prompts can be returned instantly without calling the API again. It also records simple analytics data such as timestamp, model used, execution time, and token usage. Logging is implemented to track important events and potential errors during execution.

The script also contains a small benchmarking function that can test the response time of multiple Groq models for the same prompt.

This project was created as a simple experiment to explore how an API gateway can be used to manage and monitor interactions with AI models.

To run the project, install the dependencies from `requirements.txt`, add your Groq API key in a `.env` file using the variable `GROQ_API_KEY`, and run:

python groq_gateway.py

## Sample Output

Here is a sample output of the integrated benchmarking tool, comparing latency between different Groq models:

![Groq Benchmark Results](benchmark_results.PNG)