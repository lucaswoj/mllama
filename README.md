# Mllama

Mllama is an Ollama-compatible server powered by MLX.
It leverages uses LM Studio's [`lmstudio-ai/mlx-engine`](https://github.com/lmstudio-ai/mlx-engine) to performatly serve LLM models on Apple Silicon to Ollama compatible clients.

## Features

  *	**Ollama Protocol Compatibility**: Seamlessly integrates with clients using the Ollama protocol.
  *	**Powered by MLX**: Utilizes Apple’s cutting-edge MLX framework for efficient, GPU-accelerated model execution on Apple Silicon.
  *	**Minimalism**: Is a small codebase focused on essential functionality.
  *	**OpenAPI Specification**: Provides API documentation and schemas using FastAPI’s built-in OpenAPI support.

## Installation

Install system prerequsities:
```
brew install python@3.11 make
```

Clone the repository:

```
git clone https://github.com/lucaswoj/mllama.git
cd mllama
```

Install Python dependencies:
```
make install
```

Start server:
```
make start
```

## Contributing

Contributions are welcome! Open an issue or submit a pull request with improvements or bug fixes.

## License

This project is licensed under the MIT License. See LICENSE.md for details.
