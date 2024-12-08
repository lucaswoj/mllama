```
pip install -r requirements.txt

pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## TODO

- [x] Implement model loader caching with timeout and explicit unloading
- [x] Integrate model loader with hugging face hub
- [ ] Add support for tools
- [ ] Dont download models from the chat endpoint, require use of pull
- [ ] Dynamically populate response from tags endpoint

## Later

- [ ] Add support for `template` / `raw` options
- [ ] Add support for `images` option and multimodal models
- [ ] Directly import `mlx_engine` from vendor directory without adding a symlink
- [ ] Prune unnused pip packages
- [ ] Hook up `eval_count` response field
- [ ] Fix warning `Field "model_info" in ShowModelInformationResponse has conflict with protected namespace "model_".`

## Someday Maybe

- [ ] Add support for more model options keys
- [ ] Add support for `suffix` option
- [ ] Create mypy stubs for untyped modules
