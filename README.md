```
pip install -r requirements.txt

pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## Now

- [ ] Dont download models from the chat endpoint, require use of pull
- [ ] Add custom templates and stop tokens per model
- [ ] Figure out why " #+#" is a Llama stop token
- [ ] Add more helpful log messages
- [ ] Figure out why the first words of each message seem to be getting truncated.
- [ ] Move endpoints into separate files
- [ ] Abstract out common code shared between generate and chat endpoints

## Later

- [ ] Add support for tools
- [ ] Re-enable `generate` endpoint
- [ ] Add support for `template` / `raw` options
- [ ] Add support for `images` option and multimodal models
- [ ] Directly import `mlx_engine` from vendor directory without adding a symlink
- [ ] Prune unnused pip packages
- [ ] Hook up `eval_count` response field
- [ ] Fix warning `Field "model_info" in ShowModelInformationResponse has conflict with protected namespace "model_".`
- [ ] Add support for more model options keys
- [ ] Add support for `suffix` option
- [ ] Add progress messages to pull_model endpoint
