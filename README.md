# LLM Query-Recommender

A lightweight, interactive CLI tool that parses natural-language queries, uses spaCy and a simple ambiguity classifier, and forwards questions to an Ollama-served LLaMA model for intelligent responses. Great for prototyping conversational data analysis or building recommendation bots.

## Features

* **Natural language parsing** with spaCy to extract intent and entities
* **Ambiguity detection** using a pre-trained classifier
* **Built-in handlers** for literal operations like `sort` and `group by`
* **Seamless integration** with an Ollama-hosted LLaMA model

## Prerequisites

1. **Ollama** installed on your host machine and available in `$PATH`.
2. **Docker** (Docker Desktop on macOS/Windows or native Docker on Linux).

## Quickstart

Clone the repository, build the container, start Ollama, then run the CLI:

```bash
# 1. Clone your GitHub repository
git clone https://github.com/mrizwan89/llm-query-recommender.git

# 2. Enter the project directory
cd llm-query-recommender

# 3. (macOS) Start Docker Desktop if needed
open -a Docker

# 4. Verify Docker is running
docker version

# 5. Build the Docker image
docker build -t llm-query-recommender .

# 6. In one terminal, start Ollama on your host:
ollama serve

# 7. In another terminal, run the container:
#    • macOS/Windows (uses host.docker.internal):
docker run -it --rm llm-query-recommender

#    • Linux (uses host networking):
docker run -it --rm --network host llm-query-recommender
```

You should see:

```
Query-Recommender  (type 'exit' to quit)
```

Then enter queries like:

```
Query: sort [3,1,2] in ascending
Answer:
 [1, 2, 3]
```

## Pushing to GitHub Container Registry

To make your image publicly available via GHCR:

```bash
docker tag llm-query-recommender ghcr.io/mrizwan89/llm-query-recommender:latest
docker push ghcr.io/mrizwan89/llm-query-recommender:latest
```

Anyone can then:

```bash
docker pull ghcr.io/mrizwan89/llm-query-recommender:latest
docker run -it --rm ghcr.io/mrizwan89/llm-query-recommender
```

---

Enjoy building conversational data tools with your own LLaMA-powered recommender!
