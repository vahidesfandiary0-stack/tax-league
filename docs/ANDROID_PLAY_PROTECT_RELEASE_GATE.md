# Android Play Protect release gate

This checklist is a release gate for the official RAQTIVA Android package
(`ir.raqtiva.tax_league`). A successful APK build or signature check does not
mean Google Play Protect has scanned the app or cleared its first-install warning.

## Required evidence for each official APK

- Exact APK file from the corresponding successful GitHub Actions run.
- SHA-256 checksum from the Android diagnostics artifact.
- Package ID, version code/name, SDK compatibility and requested permissions.
- APK signature verification and signer certificate SHA-256 fingerprint.
- Result of the Google Play Protect scan on a target Android device, recorded
  against the exact APK SHA-256.

## Device-side scan procedure

1. Install or open the exact release APK on a test Android device.
2. When Play Protect reports that it has not seen the app before, choose the
   offered option to send app information to Google for scanning.
3. Wait for the scan result. Record the exact warning/result, device Android
   version, date/time, and APK SHA-256.
4. If Google reports a harmful app or blocks installation, stop distribution
   and follow Google's official appeal/review process. Do not ask users to
   bypass a harmful-app verdict.
5. If the message only says the app is unknown or has not been seen before,
   record that separately. A successful signature check is not a Play Protect
   clearance and does not guarantee the warning will disappear.

## Current evidence

The CI pipeline can verify the APK signature, signer certificate, permissions,
package metadata and SHA-256. CI cannot truthfully mark the device-side
Play Protect scan as passed. That status remains pending until a scan result
is observed on a device for the exact APK hash.
