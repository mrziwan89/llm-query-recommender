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
git clone https://github.com/mrziwan89/llm-query-recommender.git

# 2. Enter the project directory
cd llm-query-recommender

# 3. (Optional) Create & activate a Python virtual environment for local development:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Install Ollama (if not already available in $PATH):
#    Download from https://ollama.com/download and follow the install instructions.

# 5. Install Docker:
#    - macOS/Windows: Download Docker Desktop from https://www.docker.com/products/docker-desktop
#    - Linux: Install Docker Engine via https://docs.docker.com/engine/install/

# 4. (macOS) Start Docker Desktop if needed
open -a Docker

# 5. Verify Docker is running
docker version

# 6. Build the Docker image
docker build -t llm-query-recommender .

# 7. In one terminal, start Ollama on your host:
ollama serve

# 8. In another terminal, run the container:
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
Direct queries are fully specified requests that the system can answer immediately without asking follow-up questions. They either invoke built-in handlers (e.g., `sort` or `group by`) or forward factual questions straight to the LLaMA model. Examples include “What is the capital of France?” or “Sort [4,2,9] in ascending order.”

```bash
Query: What is the capital of France?
Answer:
 Paris
 ```
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
Ambiguous queries lack sufficient detail or contain multiple possible intents, so the system pauses to request clarification before answering. It uses a lightweight ambiguity classifier and keyword heuristics to generate concise, targeted follow-up questions. For example, “Show me data” becomes “Which data specifically do you want to see?”

```bash
Query: Show me data
Need clarification:
 1. What does the term "data" refer to in this context? Is it referring to information, statistics, or something else?
```

```bash
Query: filter users
Need clarification:
 1. What does the term "users" refer to in this context? (e.g. people, computers, websites, etc.)
```

```bash
Query: average sum of age
Need clarification:
 1. What kind of data set are we referring to (e.g. a list of people, a dataset in a particular domain)? And what type of average would you like to calculate (e.g. mean, median, mode)?
```

### Typo & Spell-Check Handling
When user input contains typos or misspelled words, the system detects unknown terms and proposes likely corrections. It asks a simple confirmation question—e.g., “Did you mean ‘filter’?”—before proceeding. This ensures accurate parsing even with imperfect input.  
```bash
Query: shpwing me data
Need clarification:
 1. What does "shpwing" mean in this context?
```
```bash
Query: filtre users by age
Need clarification:
 1. What does "filtre" mean in this context?
 ```
