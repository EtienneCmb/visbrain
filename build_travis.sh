#!/bin/bash

if [[ "${TEST}" == "standard" ]]; then
    make test;
elif [[ "${TEST}" == "minimal" ]]; then
    make flake;
elif [[ "${TEST}" == "examples" ]]; then
    make examples;
fi
