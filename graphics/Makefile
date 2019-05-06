#####################################
# VARIABLES
#####################################

SHELL := /bin/bash

.SUFFIXES:

_E := @echo
_V := @

#####################################

.PHONY: all clean dep maintainer-clean render test

include Makefile.config

BUILD := build
SRC := src
BLEND_SRC := $(SRC)/blend

BLEND_F := $(wildcard $(BLEND_SRC)/*.blend)
BLEND_DEP := $(patsubst %.blend,$(BUILD)/%.dep,$(notdir $(BLEND_F)))

ALL_SRC := $(shell find $(SRC) -maxdepth 1 -type f) $(BLEND_F)

BLENDER_DEP_SCRIPT := $(SRC)/blender_make_deps.py
BLENDER_RENDER_SCRIPT := $(SRC)/blender_render_settings.py

BLENDER := $(shell [ $$(which blender 2> /dev/null) ] \
           && echo "blender" || echo "")

#####################################
# RULES
#####################################

# Don't try to render if blender is not found
ifneq ($(strip $(BLENDER)),)
all: render

# Don't build depencies if we are going to delete everything
ifneq ($(MAKECMDGOALS), maintainer-clean)
include $(BLEND_DEP)
endif

# Test targets
dep: $(BLEND_DEP)

# Rebuild depencies if any source file changes
$(BLEND_DEP): $(BUILD)/%.dep: $(BLEND_SRC)/%.blend \
              $(ALL_SRC) Makefile Makefile.config
	$(_E) "[GRAPHICS] [BLENDER-DEP] $< -> $@"
	$(_V) $(BLENDER) --factory-startup -noaudio --background $< \
	      --python $(BLENDER_DEP_SCRIPT) \
	      -- write_dep $@ $(BLENDER_RENDER_SCRIPT) $(render_samples) \
	      $(threads) > /dev/null

# Need to do some housekeeping, in case some files are no longer rendered
# Find what we need to keep from the .dep files
clean::
	$(_V) rm -rf $(BUILD)/trash
	$(_V) mkdir $(BUILD)/trash
	-$(_V) mv $$(grep -h -r ".png" $(BUILD)/*.dep | tr  '[ \t]' '[\n]' | \
	       tr -d '"' | grep ".png" | sort | uniq) \
	       $(BUILD)/trash > /dev/null
	$(_V) find $(BUILD) -maxdepth 1 -type f -exec rm -v {} \;
	-$(_V) mv $(BUILD)/trash/* $(BUILD) > /dev/null
	$(_V) rm -rf $(BUILD)/trash

else
all:
	$(_E) "Blender not found."
	$(_V) false
clean::
endif

maintainer-clean::
	$(_V) rm -rf $(BUILD)/*
