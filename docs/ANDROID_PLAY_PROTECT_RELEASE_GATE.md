# Android Play Protect release gate

This is the mandatory release policy for the official RAQTIVA Android package
(`ir.raqtiva.tax_league`). It records the owner-approved Android baseline and
must be followed for every future Android change.

## Owner-approved baseline (2026-11-26)

- Baseline commit: `28f7d45327031a3a3bfbf7cad0fe1bf24954bbfe`
- Baseline branch: `baseline/android-playprotect-approved-20261126`
- Source branch used to build the approved APK:
  `fix/slider-release-readiness-20261125`
- GitHub Actions Android release run: `45694002386`
- APK artifact: `tax-league-release-apk` (artifact ID `15059392851`)
- AAB artifact: `tax-league-google-play-aab` (artifact ID `15059269430`)
- Owner confirmation: installed this APK on a real Android phone; owner
  reported that the app worked correctly and Google Play Protect showed no
  warning. This is a device observation for this exact delivered build, not a
  guarantee of future Google verdicts.

Do not silently move or replace this baseline. Any new baseline requires
explicit owner approval after installation and practical testing.

## Mandatory rules for every future change

1. Start every change from the owner-approved baseline (or the latest
   explicitly owner-approved successor), never from an older release branch.
2. Keep changes minimal and scoped to the requested feature. Do not redesign,
   refactor unrelated areas, or alter stable behavior without a clear need.
3. Preserve the permanent Android application ID
   (`ir.raqtiva.tax_league`), signing identity/keystore, upload key lineage,
   versioning continuity, secure manifest defaults, and required permissions.
   Never generate or substitute a new signing key for an existing release line.
4. Do not add unnecessary SDKs, trackers, permissions, services, receivers,
   exported components, or network capabilities. Every new permission or
   dependency requires a documented technical reason and security review.
5. Do not add CafeBazaar SDK or CafeBazaar-specific release dependencies unless
   the owner explicitly authorizes them.
6. Before delivering each APK, run formatting, static analysis, all relevant
   automated tests, release configuration checks, signed release build,
   signature/signer verification, package and permission inspection, and
   Android compatibility checks. A failed or skipped required gate blocks
   delivery.
7. Produce and retain the exact APK/AAB artifacts and diagnostics from the same
   successful commit. Record commit SHA, workflow run, artifact IDs, SHA-256,
   package ID, version, signer certificate fingerprint, permissions and test
   results. Never pass an artifact from an older commit as the latest build.
8. Install and practically test the exact APK on an Android device before
   requesting owner acceptance. Ask the owner to confirm the Play Protect
   result for that exact build. CI signature success is not equivalent to a
   Play Protect scan.
9. If Play Protect reports a harmful app or blocks installation, stop
   distribution and investigate; never instruct users to bypass a harmful-app
   verdict. If Google reports only that the app is unknown, record that
   separately and follow Google's scan/review flow.
10. Do not merge, deploy to production, publish to a store, or replace the
    approved baseline without the owner's explicit authorization.

## Required evidence for each official APK

- Exact APK file from the corresponding successful GitHub Actions run.
- SHA-256 checksum and diagnostics artifact.
- Package ID, version code/name, SDK compatibility and requested permissions.
- APK signature verification and signer certificate SHA-256 fingerprint.
- Results of automated tests and practical installation checks.
- Owner-observed Google Play Protect result, recorded against the exact APK
  SHA-256 where available.

## Device-side scan procedure

1. Install or open the exact release APK on a test Android device.
2. If Play Protect offers a scan for an unfamiliar app, follow Google's
   offered scan flow.
3. Record the exact warning/result, device Android version, date/time and APK
   SHA-256.
4. If Google reports a harmful app or blocks installation, stop distribution
   and follow Google's official review process. Do not ask users to bypass a
   harmful-app verdict.
5. Treat an unknown-app notice separately from a harmful-app verdict. A
   successful signature check is not a Play Protect clearance and cannot
   guarantee that Google will never show a future warning.

## Release gate status

The CI pipeline verifies the release build, signature, package metadata,
permissions and compatibility. CI cannot independently attest to the
device-side Play Protect result. That result must be observed on a device for
the exact APK hash, and future Google decisions cannot be guaranteed.


## Current dependency review

- Payment receipt selection is restricted to one JPG, JPEG, PNG or PDF file and
  is used only inside the authenticated manual-subscription flow.
- The previous `file_picker 11.0.3` choice is withdrawn. Upstream issue
  [#2200](https://github.com/vicajilau/flutter_file_picker/issues/2200)
  documents an Android build failure on AGP 9 when `android.builtInKotlin=false`,
  affecting file_picker 11.0.1–11.0.3. The fix is in the federated 12.x line.
- The candidate now uses stable `file_picker ^12.3.0` and the v12 single-file
  API (`pickFile()`, `length()`, and `readAsBytes()`). The Dart SDK minimum
  is raised to 3.10, matching file_picker 12's Flutter 3.38 / Dart 3.10 floor.
- The Android release workflow pins Flutter 3.47.2 and explicitly keeps
  `android.builtInKotlin=false` and `android.newDsl=false`. This avoids
  prematurely enabling built-in Kotlin while remaining plugins still apply the
  legacy Kotlin Gradle plugin. Do not flip these flags to true without a full
  dependency migration and build verification.
- This is a source-level compatibility correction, not an Android release
  approval. The lockfile must be regenerated by Flutter CI; the final APK must
  still pass resolved-dependency, merged-manifest/permission, signer, package,
  SDK, diagnostic and real-device Play Protect checks before owner acceptance.

