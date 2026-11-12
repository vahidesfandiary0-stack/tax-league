#!/usr/bin/env python3
"""Configure the Flutter-generated Android Gradle project for release signing."""
from pathlib import Path
import re
import sys

gradle_file = Path(sys.argv[1] if len(sys.argv) > 1 else "android/app/build.gradle.kts")
if not gradle_file.is_file():
    raise SystemExit(f"Gradle file not found: {gradle_file}")

source = gradle_file.read_text(encoding="utf-8")
if "signingConfigs.create(\"release\")" in source:
    print("Release signing is already configured.")
    raise SystemExit(0)

android_match = re.search(r"\bandroid\s*\{", source)
if not android_match:
    raise SystemExit("Could not find the android { } block in build.gradle.kts")

opening = source.find("{", android_match.start())
depth = 0
closing = None
for index in range(opening, len(source)):
    if source[index] == "{":
        depth += 1
    elif source[index] == "}":
        depth -= 1
        if depth == 0:
            closing = index
            break
if closing is None:
    raise SystemExit("Could not locate the end of the android block")

imports = "import java.util.Properties\n\n"
if "import java.util.Properties" not in source:
    source = imports + source
    android_match = re.search(r"\bandroid\s*\{", source)
    opening = source.find("{", android_match.start())
    depth = 0
    closing = None
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                closing = index
                break

signing = """
    signingConfigs {
        create("release") {
            keyAlias = keystoreProperties["keyAlias"] as String
            keyPassword = keystoreProperties["keyPassword"] as String
            storeFile = file(keystoreProperties["storeFile"] as String)
            storePassword = keystoreProperties["storePassword"] as String
        }
    }
    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.getByName("release")
        }
    }
"""
properties = """
val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
require(keystorePropertiesFile.exists()) { "Android signing key.properties is missing" }
keystoreProperties.load(keystorePropertiesFile.inputStream())

"""
source = source[:closing] + signing + source[closing:]
# Load signing properties before the plugins/android configuration is evaluated.
plugins_match = re.search(r"\bplugins\s*\{", source)
if plugins_match:
    source = source[:plugins_match.start()] + properties + source[plugins_match.start():]
else:
    source = properties + source

gradle_file.write_text(source, encoding="utf-8")
print(f"Configured release signing in {gradle_file}")
