```
pip install -r requirements.txt
pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

## Now

- [ ] Switch to using `pip-tools`'s `requrements.in` file for dependency management or poetry
- [ ] Rename "tools" for better disambituation with LLM tools, maybe call them "scripts" or "commands"?
- [ ] Write better test suite
- [ ] Create more useful tools
- [ ] Mess around with Enchanted "completions"

## Later

- [ ] Add a system allowing scripts to be called as tools by the LLM
- [ ] Improve multhreading performance
- [ ] Ensure LLM generation is killed when the HTTP connection is aborted
- [ ] Reserch reranking systems for use with RAG and internet search
- [ ] Add more chat templates and model configurations
- [ ] Allow piping "scripts" into eachother (like /morning_report | /podcast_script | /summary)
- [ ] Try implementing "scripts" system without an intermediate process
- [ ] Create performance benchmark to test against ollama
- [ ] Restore strict mypy import checking
- [ ] Create "hooks" system to automatically run scripts at different times, allowing for - context augmentation - memories - chat history modification
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
- [ ] Ensure command processes are killed when the HTTP connection is aborted
