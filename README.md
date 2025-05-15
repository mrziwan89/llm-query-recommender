# LLM Query-Recommender

A small CLI tool that parses natural-language queries, uses spaCy + a lightweight ambiguity classifier,  
and forwards questions to an Ollama-served LLaMA model.

## Prerequisites

- **Ollama** installed on the host, running:  
  ```bash
  ollama serve --port 11434