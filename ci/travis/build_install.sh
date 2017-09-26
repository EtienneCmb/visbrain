#!/bin/bash
source activate testenv
py.test --cov --verbose
