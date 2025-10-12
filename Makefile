# simple makefile to simplify repetetive build env management tasks under posix
CTAGS ?= ctags
PYTHON ?= python
EXAMPLES_DIR ?= $(CURDIR)/examples
EXAMPLES_PNG_DIR ?= $(CURDIR)/docs/_static/examples

all: clean test

inplace:
	@python -m pip install -e .
	@python -c 'from pathlib import Path; import subprocess, sys; exec("""from pathlib import Path\nimport subprocess\nimport sys\nrequirements = []\nfor line in Path(\"requirements/base.txt\").read_text().splitlines():\n    line = line.strip()\n    if not line or line.startswith(\"#\") or set(line) == {\"=\"}:\n        continue\n    requirements.append(line)\nif requirements:\n    subprocess.check_call([sys.executable, \"-m\", \"pip\", \"install\", *requirements])\n""")'
	@python -m pip install setuptools pytest pytest-cov

clean-pyc:
	@find . -name "*.pyc" | xargs rm -f

clean-so:
	@find . -name "*.so" | xargs rm -f
	@find . -name "*.pyd" | xargs rm -f

clean-build:
	@rm -rf build

clean-ctags:
	@rm -f tags

clean-cache:
	@find . -name "__pycache__" | xargs rm -rf

clean: clean-build clean-pyc clean-so clean-ctags clean-cache
	@echo "Cleaning build, pyc, so, ctags, and cache"

clean-test: clean-build clean-pyc clean-ctags clean-cache
	@echo "Cleaning build, pyc, ctags, and cache"

test: test-nongui

test-nongui: clean-test
	@$(PYTHON) -m tox -e tests

test-gui:
	@PYTEST_MARK=gui $(PYTHON) -m tox -e tests -- --cov-append

test-html: clean-test
	@python -m pytest --cov=visbrain --cov-report=html --showlocals --durations=10 --html=report.html --self-contained-html

lint:
	@$(PYTHON) -m tox -e lint

flake: lint

qt-ui:
	@python tools/generate_qt_ui.py

qt-ui-check:
	@python tools/generate_qt_ui.py --check

examples: clean
	@$(PYTHON) tools/generate_example_gallery.py \
		--examples-dir "$(EXAMPLES_DIR)" \
		--output-dir "$(EXAMPLES_PNG_DIR)"

examples-full: examples

pypi: build_dist
	@$(PYTHON) -m twine upload --verbose dist/*


# clean dist
clean_dist:
	@rm -rf build/
	@rm -rf visbrain.egg-info/
	@rm -rf dist/
	@echo "Dist cleaned"

# build dist
build_dist: clean_dist
	@$(PYTHON) -m tox -e package
	@echo "Dist built"

# check distribution
check_dist:
	$(PYTHON) -m twine check dist/*

# upload distribution
upload_dist: build_dist
	$(PYTHON) -m twine upload --verbose dist/*
