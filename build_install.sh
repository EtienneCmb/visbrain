#!/bin/bash
source activate testenv
nosetests -v --nocapture test/
codecov