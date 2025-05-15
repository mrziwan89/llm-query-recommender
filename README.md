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

## Examples

Below are sample interactions showcasing both direct answers and clarifier questions for ambiguous inputs:

### Direct Queries

````bash
Query: What is the capital of France?
Answer:
 Paris
```bash
Query: list [10, 2, 7, 5] in descending order
Answer:
 [10, 7, 5, 2]
````

```bash
Query: Who is the president of India?
Answer:
 The President of India is Draupadi Murmu (as of 2025).
```

### Ambiguous Queries

```bash
Query: Show me data
Need clarification:
 1. Which data specifically do you want to see?
```

```bash
Query: filter users
Need clarification:
 1. What criteria should be used to filter the users?
```

```bash
Query: average revenue
Need clarification:
 1. Over what time period should I calculate the average revenue?
```

### Typo & Spell-Check Handling

```bash
Query: shpwing me data
Need clarification:
 1. Did you mean "showing"?
```
Query: filtre users by age
Need clarification:
 1. Did you mean "filter"?
