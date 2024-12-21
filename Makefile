# Makefile
clean:
	@echo "Removing Python build artifacts..."
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf build dist *.egg-info
	@echo "Clean complete!"

