# Mllama

Mllama is an Ollama-compatible server powered by MLX.
It leverages uses the same codebase as LM Studio, `lmstudio-ai/mlx-engine`, to serve powerful machine learning models performantly on Apple Silicon.

## Features

  •	Ollama Protocol Compatibility: Seamlessly integrates with clients using the Ollama protocol.
  •	Powered by MLX: Utilizes Apple’s cutting-edge MLX framework for efficient, GPU-accelerated model execution on Apple Silicon.
  •	Minimalism: Is a small codebase focused on essential functionality.
  •	OpenAPI Specification: Provides API documentation and schemas using FastAPI’s built-in OpenAPI support.

## Requirements

	•	Apple Silicon Mac (required for MLX)
	•	Python 3.11 (required by mlx-engine)

## Installation

Clone the Repository:

```
git clone https://github.com/lucaswoj/mllama.git
cd mllama
```

Create virtual environment:
```
python3.11 -m venv venv
source venv/bin/activate
```

Install Dependencies:
```
pip install -r requirements.txt
```

Start Server:
```
make start
```

## Contributing

Contributions are welcome! Open an issue or submit a pull request with improvements or bug fixes.

## License

This project is licensed under the MIT License. See LICENSE.md for details.
