PYTHON ?= python3

.PHONY: test validate check

test:
	$(PYTHON) -m unittest discover -s tests -v

validate:
	$(PYTHON) -m zhenzhi_knowledge validate

check: validate test
