
PHONIES = first all help html test flake8 git prep


first: prep

all: prep html

.PHONY: $(PHONIES)


help:
	@echo zconfigparser make file -- $(PHONIES)

html:
	$(MAKE) -C docs html

test: git
	pytest -x
	PYTHONPATH= tox

flake8: git
	flake8 .

git:
	git update-index --refresh
	git diff-index --quiet HEAD --

prep: test flake8
	@echo Done
