.PHONY: build

lint:
	@pre-commit run --all-files
