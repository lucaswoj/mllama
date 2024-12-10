echo "Testing Mllama"

urls=("http://localhost:8000/api/chat" "http://localhost:11434/api/chat")
models=("mlx-community/llama-3.3-70B-Instruct-8bit" "llama3.3:70b-instruct-q8_0")
names=("Mllama" "Ollama")

for i in "${!urls[@]}"; do
  echo "Testing ${names[$i]}"
  curl "${urls[$i]}" \
    --include \
    --header "Content-Type: application/json" \
    --data '{
      "model": "'"${models[$i]}"'",
      "messages": [
        {
          "role": "user",
          "content": "why is the sky blue? explain at a university level"
        }
      ],
      "stream": false
    }'
  echo "\n\n"
done
