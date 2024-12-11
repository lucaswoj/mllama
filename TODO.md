# Next

- [ ] Switch to using `pip-tools`'s `requrements.in` file for dependency management
- [ ] Add support for more `options` param properties on chat and generate endpoints, tune the defaults
- [ ] Add hardcoded chat templates, stop strings, and other config for models
- [ ] Write more unit tests
- [ ] Figure out why token counts are different vs Ollama
- [ ] Run performance tests against Ollama
- [ ] Create `ps` endpoint
- [ ] Create `embed` endpoint
- [ ] Create `delete` endpoint
- [ ] Create `show` endpoint
- [ ] Add support for `tools` param on chat endpoint
- [ ] Add support for `images` param on chat and generate endpoints
- [ ] Add support for `template` / `raw` param on generate endpoint
- [ ] Add support for `images` option on chat and generate endpoints
- [ ] Add support for `suffix` param on generate endpoint
- [ ] Test compatability against continue.dev
- [ ] Test compatability against OpenWebUI
- [ ] Test compatability against Enchanted

# Someday Maybe

- [ ] Measure unit test coverage
- [ ] Improve ability to handle concurrent requests
- [ ] Restore strict mypy import checking
- [ ] Annotate all pydantic BaseModel attributes with docs
- [ ] Use pydantic BaseModel Fields to specify types for all API outputs
- [ ] Add progress messages to pull endpoint
- [ ] Improve response data from tags endpoint
