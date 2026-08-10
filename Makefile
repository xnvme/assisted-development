# SPDX-FileCopyrightText: Simon A. F. Lund <os@safl.dk>
#
# SPDX-License-Identifier: BSD-3-Clause
#
# assisted-development: helper targets for installing, formatting, and testing
#
# Running "make" prints the usage below. Each target documents itself in a
# "define <target>-help" block, so the listing cannot drift from the targets.
#
.PHONY: default
default: help

define help-help
# Print this usage listing
endef
.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo ""
	@awk ' \
		/^define .*-help$$/ { \
			target = $$2; sub(/-help$$/, "", target); \
			inblock = 1; desc = ""; next \
		} \
		inblock && /^endef/ { \
			printf "  %-14s %s\n", target, desc; inblock = 0; next \
		} \
		inblock && /^#/ && desc == "" { \
			sub(/^# ?/, ""); desc = $$0; next \
		} \
	' $(MAKEFILE_LIST)
	@echo ""

define format-help
# Run the format and lint checks on every file
endef
.PHONY: format
format:
	@echo "## assisted-development: format"
	pre-commit run --all-files
	@echo "## assisted-development: format [DONE]"

define test-help
# Run the installer tests against a throwaway home directory
endef
# -B because reuse lint reports __pycache__ as files without licensing
# information, so leaving bytecode behind breaks the next "make format".
.PHONY: test
test:
	@echo "## assisted-development: test"
	python3 -B -m unittest discover -s tests -v
	@echo "## assisted-development: test [DONE]"

define install-help
# Link the conventions and skills into your agent configuration
endef
.PHONY: install
install:
	@echo "## assisted-development: install"
	./install.py
	@echo "## assisted-development: install [DONE]"

define install-dry-help
# Show what install would link, without linking anything
endef
.PHONY: install-dry
install-dry:
	@echo "## assisted-development: install-dry"
	./install.py --dry-run
	@echo "## assisted-development: install-dry [DONE]"

define uninstall-help
# Remove the links pointing at this checkout
endef
.PHONY: uninstall
uninstall:
	@echo "## assisted-development: uninstall"
	./install.py --uninstall
	@echo "## assisted-development: uninstall [DONE]"

define clean-help
# Remove generated files
endef
.PHONY: clean
clean:
	@echo "## assisted-development: clean"
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf .ruff_cache
	@echo "## assisted-development: clean [DONE]"
