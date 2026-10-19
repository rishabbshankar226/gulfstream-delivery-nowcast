PY ?= .venv/bin/python
export PYTHONPATH := src
RUN := $(PY) -m gdn

.PHONY: data design holdout snapshot nowcast lock score estimates workbook charts claims note pdf site report \
	daily-core daily all test check-determinism

data:
	$(RUN) data

design:
	$(RUN) design

holdout:
	$(RUN) holdout

snapshot:
	$(RUN) snapshot

nowcast:
	$(RUN) nowcast

lock:
	$(RUN) lock

score:
	$(RUN) score

estimates:
	$(RUN) estimates

workbook:
	$(RUN) workbook

charts:
	$(RUN) charts

claims:
	$(RUN) claims

note:
	$(RUN) note

pdf:
	$(RUN) pdf

site:
	$(RUN) site

report:
	$(RUN) report

daily-core:
	$(RUN) daily --core

daily:
	$(RUN) daily

# Offline rebuild from tracked files: no snapshot download, no SEC, no lock, no score, no live file rewritten.
all:
	$(RUN) data --offline
	$(RUN) design
	$(RUN) holdout
	$(RUN) estimates
	$(RUN) workbook
	$(RUN) charts
	$(RUN) note
	$(RUN) site
	$(RUN) report

test:
	$(PY) -m pytest -q --tb=short tests

check-determinism:
	$(PY) tools/determinism.py
