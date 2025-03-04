#!/usr/bin/env python3
import json
import os

# Define the correct order for keys
KEY_ORDER = [
    "domain",
    "name",
    "codeowners",
    "config_flow",
    "dependencies",
    "documentation",
    "iot_class",
    "issue_tracker",
    "loggers",
    "quality_scale",
    "requirements",
    "version",
]

# Path to the manifest.json file
manifest_path = os.path.join("custom_components", "rothv2", "manifest.json")

# Read the current manifest
with open(manifest_path) as f:
    manifest = json.load(f)

# Create a new ordered manifest
ordered_manifest = {}
for key in KEY_ORDER:
    if key in manifest:
        ordered_manifest[key] = manifest[key]

# Write the ordered manifest back to the file
with open(manifest_path, "w") as f:
    json.dump(ordered_manifest, f, indent=4)

print(f"Manifest file updated with keys in the correct order: {manifest_path}")
