```
pip install -r requirements.txt
pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## Now

- [ ] Switch to using `pip-tools`'s `requrements.in` file for dependency management or poetry
- [ ] Rename "tools" for better disambituation with LLM tools, maybe call them "scripts" or "commands"?
- [ ] Create more tools
- [ ] Create performance benchmark to test against Ollama

## Later

- [ ] Publish to GitHub
- [ ] Measure unit test coverage
- [ ] Define MLX engine as a "manifold", support other manifolds
- [ ] Mess around with Enchanted "completions"
- [ ] Add a system allowing scripts to be called as tools by the LLM
- [ ] Improve ability to handle concurrent requests
- [ ] Add more chat templates and model configurations
- [ ] Allow piping "scripts" into eachother (like /morning_report | /podcast_script | /summary)
- [ ] Try implementing "scripts" system without an intermediate process
- [ ] Restore strict mypy import checking
- [ ] Create "hooks" system to automatically run scripts at different times, allowing for - context augmentation - memories - chat history modification
- [ ] Annotate all BaseModel fields with docs
- [ ] Ensure all endpoints have typed response models
- [ ] Add support for `tools` param on chat endpoint
- [ ] Add support for `images` param on chat and generate endpoints
- [ ] Add support for `template` / `raw` param on generate endpoint
- [ ] Add support for `images` option on chat and generate endpoints
- [ ] Add support for more `options` param properties on chat and generate endpoints
- [ ] Add support for `suffix` param on generate endpoint
- [ ] Add progress messages to pull endpoint
- [ ] Create `ps` endpoint
- [ ] Create `embed` endpoint
- [ ] Create `delete` endpoint
- [ ] Create `show` endpoint
- [ ] Improve response data from tags endpoint
