#####################################
# VARIABLES
#####################################

SHELL := /bin/bash

.SUFFIXES:

_E := @echo
_V := @

#####################################

GRAPHICS := graphics
FEATURES := landscape trains
PROJECTS := $(GRAPHICS) $(FEATURES)

.PHONY: all clean maintainer-clean $(PROJECTS)

all: $(PROJECTS)

$(PROJECTS):
	$(MAKE) -C $@ $(MAKECMDGOALS)

# Make sure graphics are always up-to-date
$(FEATURES): $(GRAPHICS)
