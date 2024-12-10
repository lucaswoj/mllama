```
pip install -r requirements.txt
pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## Now

- [ ] Switch to using `pip-tools`'s `requrements.in` file for dependency management or poetry
- [ ] Investigate different token counts vs ollama
- [ ] Add support for more `options` param properties on chat and generate endpoints, tune the defaults
- [ ] Set up a new project for using plugins / pipelines / tools

## Later

- [ ] Publish to GitHub
- [ ] Measure unit test coverage
- [ ] Improve ability to handle concurrent requests
- [ ] Add more chat templates and model configurations
- [ ] Restore strict mypy import checking
- [ ] Annotate all BaseModel fields with docs
- [ ] Use pydantic to declare types on all outputs
- [ ] Add support for `tools` param on chat endpoint
- [ ] Add support for `images` param on chat and generate endpoints
- [ ] Add support for `template` / `raw` param on generate endpoint
- [ ] Add support for `images` option on chat and generate endpoints
- [ ] Add support for `suffix` param on generate endpoint
- [ ] Add progress messages to pull endpoint
- [ ] Create `ps` endpoint
- [ ] Create `embed` endpoint
- [ ] Create `delete` endpoint
- [ ] Create `show` endpoint
- [ ] Improve response data from tags endpoint
