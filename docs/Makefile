# Simplified Makefile for Sphinx documentation builds

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     := $(CURDIR)
BUILDDIR      := $(abspath $(CURDIR)/../_build/docs)
DOCTREES      := $(BUILDDIR)/doctrees
HTMLDIR       := $(BUILDDIR)/html

.PHONY: help clean html linkcheck doctest

help:
	@echo "Please use `make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files (warnings are treated as errors)"
	@echo "  clean      to remove the generated documentation artifacts"
	@echo "  linkcheck  to check all external links for integrity"
	@echo "  doctest    to run doctests embedded in the documentation"

clean:
	rm -rf $(BUILDDIR)

html:
	$(SPHINXBUILD) -b html -W --keep-going $(SPHINXOPTS) -d $(DOCTREES) $(SOURCEDIR) $(HTMLDIR)
	@python example_to_thumbnails.py
	@echo
	@echo "Build finished. The HTML pages are in $(HTMLDIR)."

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(SPHINXOPTS) -d $(DOCTREES) $(SOURCEDIR) $(BUILDDIR)/linkcheck

doctest:
	$(SPHINXBUILD) -b doctest $(SPHINXOPTS) -d $(DOCTREES) $(SOURCEDIR) $(BUILDDIR)/doctest
