# MiricleDrive Scanner

## Operating Spec v0

The scanner does not understand the archive.

The scanner proves what exists.

MiricleDrive Scanner v0 is the first executable witness layer for the MiricleDrive provenance-preserving cognition archive. It walks a source folder, hashes files, records timestamps, classifies basic artifact types, detects exact duplicates, and emits witness-grade manifest outputs.

It does not summarize.  
It does not interpret.  
It does not delete.  
It does not render a person.  
It does not fill gaps.

It observes, hashes, timestamps, classifies, and records.

## Core Boundary

The scanner is a preservation kernel, not a reasoning engine.

Its duty is to establish baseline evidence:

- what exists
- where it was observed
- how large it is
- what its hash is
- what timestamps are visible
- what source context is available
- what type it appears to be
- whether it can be read
- whether exact duplicates exist
- whether the artifact appears related to augmented AI thought

The scanner must not claim what the artifact means.

## Usage

```bash
python miricledrive/scanner/scan.py /path/to/source --output /path/to/output --source-label "External Drive A"
```

Optional directory markers:

```bash
python miricledrive/scanner/scan.py /path/to/source --output /path/to/output --include-dirs
```

## Current Outputs

The scanner currently emits:

```text
manifest.ndjson
duplicates.json
fixity-baseline.txt
ingest-events.ndjson
```

### manifest.ndjson

One newline-delimited JSON record per discovered file or directory marker.

Each record follows the general shape of:

```text
miricledrive/schema/json/artifact.manifest.schema.json
```

### duplicates.json

Exact duplicate groups based on SHA-256 hash.

This is logical deduplication only.

No files are deleted.

### fixity-baseline.txt

A checksum baseline in the format:

```text
sha256  normalized/path
```

This is the first fixity reference for later verification.

### ingest-events.ndjson

A scanner-level ingest event recording the scan result, run ID, output paths, host, platform, record count, and non-invention boundary.

## Current Limitations

Scanner v0 does not yet:

- validate output against the JSON Schema
- emit a separate errors.ndjson file
- emit explicit scan-start and scan-end events
- extract EXIF metadata
- extract media duration or codec metadata
- inspect archive contents
- process nested archives
- compute BLAKE3 hashes
- distinguish all observed fields from guessed fields cleanly
- parse AI conversation exports into cognition-thread schema
- create PREMIS-compatible event records
- write to SQL
- build a provenance graph
- generate timelines
- render retrieval bundles

These limitations are intentional at v0.

The first executable step is baseline observation.

## v1 Corrections

The next version should add:

1. `errors.ndjson` as a first-class output.
2. Explicit `scan_started` and `scan_completed` events.
3. JSON Schema validation for manifest records.
4. Stronger separation of observed fields and guessed fields.
5. Optional BLAKE3 hashing.
6. Archive member expansion without destructive extraction.
7. EXIF and media metadata extraction.
8. AI conversation export parsers.
9. Fixity recheck mode.
10. PREMIS-inspired object, event, and agent records.

## Preservation Principles

Fixity is the bedrock.

A checksum is not meaning, but it is the first defense against silent loss.

A duplicate is not trash by default.

A copied archive may be a preservation event.

A timestamp is evidence, not truth.

A filename hint is a guess, not provenance.

A path containing an AI platform name is not proof of platform origin.

Unknown remains unknown.

## Augmented AI Thought Handling

Since late 2024, the MiricleDrive corpus includes not only ordinary files and media but also augmented AI thought artifacts:

- prompts
- AI responses
- human-AI threads
- reasoning exports
- correction events
- model comparisons
- research notes
- tool traces
- schema formation
- doctrine formation
- code formation

The scanner marks likely AI-related artifacts but does not claim authenticity.

Future parsers must normalize these into:

```text
miricledrive/schema/json/cognition.thread.schema.json
```

Core rule:

An AI response has no continuity authority until a human adjudication event attaches to it.

## Ethical Boundary

The scanner is allowed to say:

- this file exists
- this file was observed at this path
- this file has this hash
- this file appears readable
- this file appears duplicated by hash
- this file appears to be a video, document, archive, or AI-related artifact
- this timestamp was observed from the filesystem

The scanner is not allowed to say:

- this file mattered
- this file did not matter
- this is the true version of a person
- this duplicate has no meaning
- this gap should be filled
- this archive can be safely forgotten

Meaning remains outside the scanner.

## Project Position

MiricleDrive is not a chatbot over files.

MiricleDrive is not a personality engine.

MiricleDrive is not a consciousness upload system.

MiricleDrive is a provenance-preserving cognition archive.

The scanner is the first executable component.

It makes preserved reality legible and accountable to future intelligence through manifests, checksums, provenance, and uncertainty labels.

## First Milestone

The first real milestone is simple:

Point the scanner at a real drive and produce a verifiable manifest package.

When that happens, MiricleDrive stops describing preserved reality and starts inventorying it.
