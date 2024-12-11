# Mllama

Mllama is an Ollama-compatible server powered by MLX.
It leverages uses LM Studio's [`lmstudio-ai/mlx-engine`](https://github.com/lmstudio-ai/mlx-engine) to performatly serve LLM models on Apple Silicon to Ollama compatible clients.

## Features

  *	**Ollama Compatibility**: Seamlessly integrates all clients that support the Ollama protocol.
  *	**Powered by MLX**: Uses Apple’s MLX framework for cutting-edge performance on Apple Silicon. Prompt evaluation time is signficiantly faster than on Ollama.

## Development Status

This project is in early development but is able to support simple chat clients, such as Enchanted, without issue. See `TODO.md` for open tasks.

## Installation

Clone the repository:

```
git clone https://github.com/lucaswoj/mllama.git
cd mllama
```

Install dependencies:
```
brew install make
make install
```

Start server:
```
make start
```

## Contributing

Contributions are welcome! Open an issue or submit a pull request with improvements or bug fixes. Be nice.

## License

This project is licensed under the MIT License. See LICENSE.md for details.
