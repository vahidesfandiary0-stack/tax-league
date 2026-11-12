#!/usr/bin/env python3
"""Configure a Flutter-generated Kotlin Gradle file for release signing."""
from pathlib import Path
import re
import sys

gradle_file = Path(sys.argv[1] if len(sys.argv) > 1 else "android/app/build.gradle.kts")
if not gradle_file.is_file():
    raise SystemExit(f"Gradle file not found: {gradle_file}")
source = gradle_file.read_text(encoding="utf-8")
if 'create("release")' in source and "keystorePropertiesFile" in source:
    print("Release signing is already configured.")
    raise SystemExit(0)

def block_end(text, opening):
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise SystemExit("Unbalanced Gradle block")

plugins = re.search(r"\bplugins\s*\{", source)
android = re.search(r"\bandroid\s*\{", source)
if not plugins or not android:
    raise SystemExit("Expected plugins { } and android { } blocks in build.gradle.kts")
plugins_open = source.find("{", plugins.start())
plugins_close = block_end(source, plugins_open)
android = re.search(r"\bandroid\s*\{", source)
android_open = source.find("{", android.start())
android_close = block_end(source, android_open)

if "import java.util.Properties" not in source:
    source = "import java.util.Properties\\n\\n" + source
    plugins = re.search(r"\bplugins\s*\{", source)
    plugins_open = source.find("{", plugins.start())
    plugins_close = block_end(source, plugins_open)
    android = re.search(r"\bandroid\s*\{", source)
    android_open = source.find("{", android.start())
    android_close = block_end(source, android_open)

properties = """
val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
require(keystorePropertiesFile.exists()) { "Android signing key.properties is missing" }
keystoreProperties.load(keystorePropertiesFile.inputStream())

"""
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
source = source[:android_close] + signing + source[android_close:]
# Recalculate plugins block after the Android block insertion.
plugins = re.search(r"\bplugins\s*\{", source)
plugins_open = source.find("{", plugins.start())
plugins_close = block_end(source, plugins_open) + 1
source = source[:plugins_close] + "\n\\n" + properties + source[plugins_close:]
gradle_file.write_text(source, encoding="utf-8")
print(f"Configured release signing in {gradle_file}")
