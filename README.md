```
pip install -r requirements.txt

pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## Now

- [ ] Add more helpful console log messages
- [ ] Figure out why the first words of each message seem to be getting truncated. https://github.com/lmstudio-ai/mlx-engine/issues/42
- [ ] Move each endpoint into a separate file
- [ ] Create pipelines system, use it to implement slash commands
- [ ] Try OpenWebUI integration
- [ ] Nest all packages under pal. namespace

## Later

- [ ] Figure out why " #+#" is a Llama stop token
- [ ] Add support for `tools` on chat endpoint
- [ ] Add support for `template` / `raw` options on generate endpoint
- [ ] Add support for `images` option on chat and generate endpoints
- [ ] Directly import `mlx_engine` from vendor directory without adding a symlink
- [ ] Prune unnused pip packages
- [ ] Fix warning `Field "model_info" in ShowModelInformationResponse has conflict with protected namespace "model_".`
- [ ] Hook up `eval_count` response field on chat and generate endpoints
- [ ] Add support for more options on chat and generate endpoints
- [ ] Add support for `suffix` option on generate endpoint
- [ ] Add progress messages to pull endpoint
- [ ] Create `ps` endpoint
- [ ] Create `embed` endpoint
- [ ] Create `delete` endpoint
- [ ] Create `show` endpoint
- [ ] Improve response data from tags endpoint
- [ ] Firmly turn off `create`, `push` and `copy` endpoints
