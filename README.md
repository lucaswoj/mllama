```
pip install -r requirements.txt

pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## TODO

- [ ] Directly import `mlx_engine` from vendor directory without adding a symlink
- [ ] Implement model loader caching with timeout and explicit unloading
- [ ] Integrate model loader with hugging face hub
- [ ] Add support for multimodal models with images
- [ ] Add support for template / raw options
- [ ] Add support for more model options keys
- [ ] Hook up `eval_count` parameter
- [ ] Add more unit tests
- [ ] Fix warning `Field "model_info" in ShowModelInformationResponse has conflict with protected namespace "model_".`
- [ ] Prune unnused pip packages
