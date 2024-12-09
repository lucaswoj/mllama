```
pip install -r requirements.txt
pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## Now

- [ ] Do self code review
- [ ] Create better model info repository
- [ ] Create separate driver methods for loading, unloading, and generating
- [ ] Create pipelines system, use it to implement slash commands

## Later

- [ ] Add support for `tools` on chat endpoint
- [ ] Nest all packages under `pal` namespace
- [ ] Directly import `mlx_engine` from vendor directory without adding a symlink
- [ ] Try OpenWebUI integration
- [ ] Add more helpful console log messages
- [ ] Add support for `template` / `raw` options on generate endpoint
- [ ] Add support for `images` option on chat and generate endpoints
- [ ] Prune unnused pip packages
- [ ] Fix warning `Field "model_info" in ShowModelInformationResponse has conflict with protected namespace "model_".`
- [ ] Add support for more options on chat and generate endpoints
- [ ] Add support for `suffix` option on generate endpoint
- [ ] Add progress messages to pull endpoint
- [ ] Create `ps` endpoint
- [ ] Create `embed` endpoint
- [ ] Create `delete` endpoint
- [ ] Create `show` endpoint
- [ ] Improve response data from tags endpoint
- [ ] Firmly turn off `create`, `push` and `copy` endpoints
- [ ] Add llm-structured-output driver
- [ ] Restore strict mypy import checking
