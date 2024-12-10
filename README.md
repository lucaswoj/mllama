```
pip install -r requirements.txt
pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## Now

- [ ] Create pipelines system, use it to implement slash commands
- [ ] Add more chat templates for different models
- [ ] Figure out better package management system
- [ ] Write better test suite
- [ ] Remove "full_response" property from EndEvent
- [ ] Make tools stream their output

## Later

- [ ] Create performance benchmark to test against ollama
- [ ] Improve multhreading performance
- [ ] Restore strict mypy import checking
- [ ] Annotate all BaseModel fields with docs
- [ ] Ensure all endpoints have typed response models
- [ ] Add support for `tools` on chat endpoint
- [ ] Add support for `images` on chat endpoint
- [ ] Add support for `images` on generate endpoint
- [ ] Try OpenWebUI integration
- [ ] Add more helpful console log messages
- [ ] Add support for `template` / `raw` options on generate endpoint
- [ ] Add support for `images` option on chat and generate endpoints
- [ ] Prune unnused pip packages
- [ ] Add support for more options on chat and generate endpoints
- [ ] Add support for `suffix` option on generate endpoint
- [ ] Add progress messages to pull endpoint
- [ ] Create `ps` endpoint
- [ ] Create `embed` endpoint
- [ ] Create `delete` endpoint
- [ ] Create `show` endpoint
- [ ] Improve response data from tags endpoint
- [ ] Add llm-structured-output driver
