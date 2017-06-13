#!/bin/bash
source activate testenv
nosetests -v --nocapture --with-coverage test/
