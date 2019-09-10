# simple makefile to simplify repetetive build env management tasks under posix
CTAGS ?= ctags

all: clean inplace test

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

test: clean-test
	@python setup.py test
	@coverage report

test-html: clean-test
	@py.test --cov-report html --showlocals --durations=10 --html=report.html --self-contained-html

flake: clean-test
	@flake8

examples: clean
	@for i in examples/brain/*.py examples/objects/*.py;do \
		echo "-----------------------------------------------"; \
		echo $$i; \
		echo "-----------------------------------------------"; \
		python $$i --visbrain-show=False; \
		echo "\n"; \
	done

examples-full: clean
	@for i in @for i in examples/*/*.py;do \
		echo "-----------------------------------------------"; \
		echo $$i; \
		echo "-----------------------------------------------"; \
		python $$i --visbrain-show=False; \
		echo "\n"; \
	done

pypi:
	@python setup.py register -r pypi
	@python setup.py sdist upload -r pypi


# clean dist
clean_dist:
	@rm -rf build/
	@rm -rf build/
	@rm -rf visbrain.egg-info/
	@rm -rf dist/
	@echo "Dist cleaned"

# build dist
build_dist: clean_dist
	python setup.py sdist
	python setup.py bdist_wheel
	@echo "Dist built"

# check distribution
check_dist:
	twine check dist/*

# upload distribution
upload_dist:
	twine upload --verbose dist/*
