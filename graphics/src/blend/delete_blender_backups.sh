#!/bin/bash

# Remove blender backup files with confirmation
find . -name "*.blend?" -type f -exec rm -i "{}" \;
