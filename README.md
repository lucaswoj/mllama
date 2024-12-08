```
pip install -r requirements.txt

pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## TODO

- [ ] Implement model loader caching with timeout and explicit unloading
- [ ] Integrate model loader with hugging face hub

## Later

- [ ] Directly import `mlx_engine` from vendor directory without adding a symlink
- [ ] Prune unnused pip packages
- [ ] Hook up `eval_count` response field
- [ ] Fix warning `Field "model_info" in ShowModelInformationResponse has conflict with protected namespace "model_".`
- [ ] Add support for template / raw options

## Someday Maybe

- [ ] Add support for more model options keys
- [ ] Add support for `suffix` option
- [ ] Add support for `images` option and multimodal models
