#!/bin/bash
source activate testenv
py.test --cov --verbose
visbrain_sleep --downsample 50
