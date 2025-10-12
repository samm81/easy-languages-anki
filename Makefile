# https://tech.davis-hansson.com/p/make/
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# ANSI color codes
GREEN=$(shell tput -Txterm setaf 2)
YELLOW=$(shell tput -Txterm setaf 3)
RED=$(shell tput -Txterm setaf 1)
BLUE=$(shell tput -Txterm setaf 6)
RESET=$(shell tput -Txterm sgr0)

# !! `Makefile` must use tabs !!

# first command is what get runs by default

.PHONY: setup
setup:
	python -m spacy download es_core_news_md

.PHONY: lint/check
lint/check:
	ruff check

.PHONY: lint/fix
lint/fix:
	ruff fix

.PHONY: vocab-expander
vocab-expander:
	env PYTHONPATH="./src:$PYTHONPATH" ./scripts/vocab-expander.py
