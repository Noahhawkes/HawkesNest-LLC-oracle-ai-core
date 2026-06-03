# MiricleDrive: Provenance-First Schema

## Data Model for an Evidence-Preserving Continuity System

Status: Working schema specification  
Purpose: Define the first data-layer model for MiricleDrive so provenance, uncertainty, and non-invention are enforceable below the prompt layer.

## 1. Core Contract

MiricleDrive is an evidence-preserving continuity system.

Its core contract is provenance, not personality.

The system does not begin by summarizing a person, generating a biography, or creating an avatar.

It begins by preserving physical memory artifacts and making every later interpretation auditable back to source.

The data layer must enforce this distinction.

## 2. System Shape

MiricleDrive should be modeled as a hybrid of:

- archive catalog
- provenance graph
- fixity ledger
- evidence claim registry
- uncertainty map
- retrieval bundle system

Raw artifacts are primary entities.

Transforms are explicit activities.

Humans, devices, software, and models are agents.

Every surfaced claim must be linked to evidence status and source links.

## 3. Top-Level Domains

Minimum top-level domains:

- artifacts: preserved things such as videos, photos, messages, files, exports, disk images, transcripts, logs, and backups
- activities: ingest, copy, hash, OCR, transcription, deduplication, restoration, annotation, retrieval render
- agents: human builder, reviewer, device, software model, pipeline service, external system
- claims: typed assertions surfaced by the system, each with evidence level and support links
- copies_and_fixity: where copies live, what checksum each copy has, when it was last verified, and whether it passed
- time_assertions: separate time claims with source, confidence, and uncertainty
- retrieval_bundles: reproducible sets of evidence returned in response to a query

## 4. Minimal v1 Tables

The smallest buildable version should start with ten tables:

1. artifact
2. artifact_copy
3. activity
4. agent
5. activity_input
6. activity_output
7. claim
8. claim_evidence
9. time_assertion
10. fixity_event

These are enough to ingest originals, preserve duplicates, derive transcripts, track provenance, represent uncertainty, and stop the renderer from inventing unsupported continuity.

## 5. Artifact Table

The artifact table represents one logical archival object.

Distinct stored instances belong in artifact_copy so content can be deduplicated without erasing storage history.

Suggested fields:

```text
artifact
- artifact_id UUID primary key
- artifact_type enum(video, image, audio, document, message_export, disk_image, backup_set, transcript, embedding, note, log, other)
- preservation_class enum(original, preservation_master, access_copy, derivative, inferred_record)
- title text
- original_filename text
- extension text
- mime_type text
- byte_size integer
- root_content_hash text
- canonical_hash_algo text
- bag_id_or_package_id text nullable
- source_id text nullable
- capture_device_id text nullable
- created_at_claimed timestamp nullable
- created_at_observed timestamp nullable
- ingested_at timestamp not null
- timezone_context text nullable
- format_risk_level enum(low, medium, high, unknown)
- corruption_status enum(unknown, clean, damaged, partial, unreadable)
- access_restriction enum(open, private, restricted, sealed)
- description text nullable
- metadata_json jsonb
```

Rule: originals and derivatives must never be collapsed into one row.

A transcript is not the same thing as the audio it came from.

A proxy is not the same thing as the raw video master.

## 6. Artifact Copy Table

Artifact copies represent physical or cloud-preserved instances of an artifact.

```text
artifact_copy
- copy_id UUID primary key
- artifact_id UUID references artifact(artifact_id)
- storage_location_id UUID
- path_or_key text
- storage_medium enum(ssd, hdd, tape, cloud_object, optical, offline_vault, unknown)
- copy_hash text
- hash_algo text
- captured_from_copy_id UUID nullable
- written_at timestamp nullable
- last_seen_at timestamp nullable
- last_verified_at timestamp nullable
- is_air_gapped boolean
- write_protected boolean
- encryption_state enum(unencrypted, encrypted, unknown)
- preservation_role enum(primary, secondary, offsite, cold, escrow, unknown)
- health_status enum(unknown, healthy, degraded, missing, failed)
- verification_status enum(unknown, pass, fail, unreadable, partial)
```

Copies are not clutter by default.

Copies are provenance.

## 7. Activity Table

Activities represent any process that acts on artifacts.

```text
activity
- activity_id UUID primary key
- activity_type enum(ingest, copy, hash, verify_fixity, ocr, asr, transcode, extract_metadata, deduplicate, restore, annotate, retrieve, render, human_review, other)
- started_at timestamp
- ended_at timestamp nullable
- performed_by_agent_id UUID references agent(agent_id)
- software_version text nullable
- parameters_json jsonb
- determinism_level enum(deterministic, probabilistic, human, mixed, unknown)
```

Every transformation must be an activity.

No derived artifact should exist without a generating activity.

## 8. Agent Table

Agents represent humans, devices, organizations, software tools, models, and pipeline services.

```text
agent
- agent_id UUID primary key
- agent_type enum(human, organization, device, software, model, pipeline_service, external_system, unknown)
- name text
- version text nullable
- manufacturer text nullable
- trust_class enum(primary_human, trusted_device, trusted_software, untrusted, unknown)
- notes text nullable
```

Agents make accountability explicit.

The system should know whether an artifact came from a camera, phone, model, person, cloud export, or unknown source.

## 9. Provenance Edge Tables

Use explicit edge tables to represent provenance relationships.

```text
activity_input
- activity_id UUID references activity(activity_id)
- artifact_id UUID references artifact(artifact_id)
- role enum(source, reference, sidecar, manifest, prior_copy)
```

```text
activity_output
- activity_id UUID references activity(activity_id)
- artifact_id UUID references artifact(artifact_id)
- role enum(master, derivative, report, transcript, thumbnail, repaired_copy, proxy, manifest)
```

```text
activity_agent
- activity_id UUID references activity(activity_id)
- agent_id UUID references agent(agent_id)
- role enum(operator, reviewer, software, capture_device, source_system)
```

Optional v2 table:

```text
artifact_relation
- from_artifact_id UUID references artifact(artifact_id)
- to_artifact_id UUID references artifact(artifact_id)
- relation_type enum(duplicate_of, near_duplicate_of, derived_from, packaged_with, excerpt_of, restored_from, contradicts, supersedes)
- asserted_by_activity_id UUID references activity(activity_id)
```

## 10. Claim Table

Claims are typed statements the system may surface.

The claim layer is where truth status becomes enforceable.

```text
claim
- claim_id UUID primary key
- claim_type enum(fact, classification, temporal_estimate, identity_link, contradiction_notice, gap_notice, summary_fragment)
- claim_text text
- subject_ref text nullable
- predicate text nullable
- object_ref_or_literal text nullable
- evidence_level enum(recorded, derived, inferred, uncertain, missing, forbidden)
- confidence_score numeric nullable
- confidence_basis enum(rule, model, human, mixed, none)
- human_review_status enum(unreviewed, approved, rejected, contested)
- contradiction_group_id UUID nullable
- valid_from timestamp nullable
- valid_to timestamp nullable
- renderer_visibility enum(allowed, restricted, blocked)
- forbidden_if_unverified boolean
- created_by_activity_id UUID references activity(activity_id)
```

A renderer should only present a claim if renderer_visibility allows it and the claim has enough linked evidence for its evidence level.

This is the mechanism that blocks counterfeit authorship from slipping in as fluent prose.

## 11. Claim Evidence Table

Claims require support links.

```text
claim_evidence
- claim_id UUID references claim(claim_id)
- artifact_id UUID nullable references artifact(artifact_id)
- activity_id UUID nullable references activity(activity_id)
- support_type enum(direct_quote, frame_span, transcript_span, metadata_field, checksum_manifest, human_note, model_output)
- locator_json jsonb
- weight numeric nullable
```

Examples of locator_json:

- byte range
- video timecode span
- transcript segment ID
- frame interval
- document paragraph range
- message ID
- metadata key path

## 12. Truth-Status Levels

Every claim must carry one of these levels:

recorded: Directly present in a preserved artifact.

derived: Produced from recorded data by a transformation such as transcript, OCR, embedding, count, or cluster.

inferred: Higher-order interpretation that requires uncertainty labeling and review.

uncertain: Conflicting evidence or insufficient confidence.

missing: Expected or relevant evidence is absent.

forbidden: The system is configured not to invent or infer in this domain.

The renderer must not emit untyped narrative text.

Every statement must have a truth-status level.

## 13. Time Assertion Table

Time is evidence, not a single unquestioned column.

```text
time_assertion
- time_assertion_id UUID primary key
- artifact_id UUID references artifact(artifact_id)
- asserted_time_start timestamp nullable
- asserted_time_end timestamp nullable
- assertion_type enum(filesystem_mtime, filesystem_ctime, exif_capture, message_header, ingest_time, filename_date, inferred_window, human_annotation)
- source_artifact_id UUID nullable references artifact(artifact_id)
- confidence_score numeric
- timezone text nullable
- asserted_by_activity_id UUID references activity(activity_id)
```

Timeline construction must preserve timestamp conflicts.

A filename date is not an EXIF timestamp.

A file modified time is not a capture time.

Unknown remains unknown.

## 14. Fixity Event Table

Fixity is mandatory for continuity preservation.

```text
fixity_event
- fixity_event_id UUID primary key
- copy_id UUID references artifact_copy(copy_id)
- checked_at timestamp
- checker_agent_id UUID references agent(agent_id)
- expected_hash text
- observed_hash text
- result enum(pass, fail, unreadable, partial)
- check_scope enum(full, spot, manifest)
- repair_source_copy_id UUID nullable references artifact_copy(copy_id)
- notes text nullable
```

A fixity failure must create an immutable event.

The system may not silently overwrite or repair without a record.

## 15. Retrieval Bundle Table

A retrieval bundle is a reproducible evidence set returned for a query.

```text
retrieval_bundle
- retrieval_id UUID primary key
- query_text text
- requested_by_agent_id UUID references agent(agent_id)
- generated_at timestamp
- included_artifact_ids UUID[]
- included_claim_ids UUID[]
- excluded_claim_ids UUID[]
- uncertainty_notices jsonb
- contradiction_notices jsonb
- missing_data_notices jsonb
- render_policy enum(inventory_only, evidence_table, human_review_required, blocked)
```

This makes every answer reproducible.

Same query.

Same included evidence set.

Same visible gaps.

## 16. Enforcement Rules

The schema becomes meaningful only when rules are enforced at write time and render time.

Minimum rules:

- A derived artifact must reference at least one parent artifact and one generating activity.
- An inferred claim cannot exist without linked supporting artifacts or claims plus a confidence score.
- A recorded claim must point directly to an original or preservation-master artifact span, not only to another claim.
- A fixity failure must create an immutable fixity_event.
- The system may not silently overwrite a damaged copy.
- A contradiction must be stored as parallel claims in the same contradiction_group_id, not resolved automatically.
- Any claim marked forbidden or forbidden_if_unverified is blocked from narrative rendering.
- AI-derived interpretations must never be written back as primary source artifacts.
- Proxy artifacts must never replace raw masters.
- Missing data must be represented as missing, not filled.

## 17. Example Flow

A POV video clip is imported from a camera card as an original artifact with a root SHA-256 hash.

Two stored copies are created: one local and one offsite.

A transcription activity uses the video artifact and emits a transcript artifact.

A claim such as "speaker says we are moving tomorrow" can be marked recorded only if linked to a transcript span and the original audio timecode.

A claim such as "this was a major life transition" remains inferred and review-gated.

The system can retrieve both claims, but it must not collapse them into one truth level.

## 18. Build Recommendation

Next build target:

- SQL schema v1
- migrations folder
- sample seed data
- ingestion manifest JSON schema
- CLI stub for file inventory

Suggested repository path:

```text
miricledrive/
  schema/
    sql/
      001_core_tables.sql
    json/
      artifact.manifest.schema.json
  docs/
    provenance-first-schema.md
```

## 19. Final Principle

The archive is physical memory in ore form.

The schema is the first refinery.

No rendering without provenance.

No inference without evidence status.

No continuity without source linkage.

No AI authorship over the human origin.
