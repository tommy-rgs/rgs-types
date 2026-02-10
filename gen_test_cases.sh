#!/bin/bash

poetry run rgs-gen test_cases/**/*.json --lang cpp --output build/cpp
poetry run rgs-gen test_cases/**/*.json --lang typescript --output build/typescript
poetry run rgs-gen test_cases/**/*.json --lang python --output build/python