# MiricleDrive: Protocol Governance Primitives

## From Policy Layer to Protocol Layer

Status: Working protocol specification  
Purpose: Define the next governance primitives required to move MiricleDrive from asserted policy to enforceable protocol.

## 1. Core Correction

MiricleDrive has governance design.

The missing layer is protocol enforcement.

The 51/49 rule, epistemic classes, human adjudication, and non-invention boundaries are governance policy.

They become enforceable only when they are represented as cryptographically bound protocol events.

Policy says what should happen.

Protocol constrains what can happen.

## 2. Central Design Problem

The current system can assert:

- human retained authority
- AI remained witness
- promotion occurred
- artifact was preserved
- deletion did not happen
- provenance was maintained

The next system must prove:

- who asserted it
- what exact envelope was asserted
- when it was asserted
- what ledger state it extended
- whether the signer had authority at that time
- whether the event was later superseded, redacted, or challenged

## 3. Unified Envelope Primitive

The generation envelope, canonicalization unit, and signed object must be the same object.

For cognition artifacts, hashing response text alone is insufficient.

A response hash proves the text existed.

It does not prove how the response came to be.

A cognition artifact must include the full generation envelope:

- prompt hash
- response hash
- system prompt hash when available
- upstream context hashes
- model provider
- model name
- model version or version status
- parameters when available
- tool call hashes
- source export hash
- platform conversation identifiers when available
- timestamp claims
- reproducibility status
- human adjudication status

This envelope is:

1. The canonical object to serialize.
2. The object to hash.
3. The object human signatures bind to.
4. The object ledger events reference.

## 4. Canonicalization Rule

Structured cognition artifacts must be canonicalized before hashing or signing.

Without canonicalization, semantically identical records may produce different hashes because of:

- key order
- whitespace
- Unicode normalization
- timestamp formatting
- null handling
- array ordering

MiricleDrive should use a formal canonical JSON rule before computing envelope hashes.

Until canonicalization is implemented, envelope hashes must be marked provisional.

## 5. Reproducibility Status

Hosted AI outputs are usually not reproducible.

Even with prompt and response hashes, the system may not know:

- exact model weights
- hidden system prompt
- hidden routing
- seed
- sampling behavior
- model revision
- safety transformation layer
- retrieval context

Therefore cognition artifacts must explicitly carry reproducibility status:

- reproducible
- partially_reproducible
- not_reproducible
- unknown

This prevents clean fixity from creating false confidence.

## 6. Manifest Chain Primitive

Leaf fixity is not ledger integrity.

Hashing files proves a file state.

It does not prevent deletion, rewriting, or reordering of manifest events.

MiricleDrive requires a tamper-evident manifest chain.

Each event should include:

- event_id
- event_type
- canonical_event_hash
- prior_ledger_head
- new_ledger_head
- timestamp
- actor_id
- event_payload_hash

A process may append.

A process may not silently rewrite.

A missing event must be detectable.

## 7. External Anchoring

A local hash chain protects against accidental mutation and some tampering.

It does not prove the chain existed at a given outside time.

MiricleDrive should support optional external anchoring:

- RFC 3161 timestamping
- transparency log anchoring
- public-chain hash anchoring
- signed offsite witness copy

The archive does not need to expose private content externally.

It only needs to anchor ledger roots.

## 8. Signed Promotion Primitive

Human promotion cannot be only a field.

A daemon could fabricate a field.

Promotion must be a signed event.

The signed promotion must bind to:

- canonical generation envelope hash
- prior ledger head
- adjudication type
- signer key id
- signer authority role
- timestamp
- promotion scope

Signing only an artifact_id is not enough.

An id can be replayed onto a different lineage.

The signature must bind the complete envelope and current chain state.

## 9. Key Isolation

Signed promotion is only as sovereign as key custody.

If the signing key lives on the same always-on system as the daemon, the daemon can be compromised and sign as the human authority.

Therefore MiricleDrive must support key isolation:

- hardware security key
- separate device signing
- offline signing
- out-of-band confirmation
- key never held by daemon process

The daemon may prepare a promotion request.

The daemon may not hold the promotion key.

## 10. Agenda Capture Problem

Signed promotion secures the final act.

It does not secure the choice set.

If the daemon decides what enters the human review queue, sovereignty can be captured upstream.

The review threshold becomes the actual sovereign.

Therefore the daemon must not silently decide without surfacing.

Required controls:

- human-set thresholds
- threshold change log
- auditable queue construction
- defer-for-later-review state
- no silent final disposition by machine choice
- random sampling of non-surfaced items
- periodic queue audit reports

The system may prioritize.

It may not disappear evidence from human visibility.

## 11. Review Queue Primitive

Every artifact or cognition event must enter one of these states:

- not_reviewed
- queued_for_review
- deferred_for_later_review
- human_promoted
- human_rejected
- human_sealed
- tombstoned
- blocked

Machine confidence may influence priority.

Machine confidence may not erase the need for traceability.

## 12. State Machine for Epistemic Classes

Epistemic classes are not only labels.

They require guarded transitions.

Classes:

- recorded
- derived
- inferred
- uncertain
- missing
- forbidden

Required transition controls:

- who may set the class
- what evidence is required
- whether transition is reversible
- whether human review is required
- whether the transition creates a ledger event
- whether the class blocks rendering

Example:

uncertain -> recorded requires direct source evidence and human or rule-based verification.

inferred -> recorded is forbidden unless new direct evidence is attached.

forbidden -> renderable requires explicit signed human policy change.

## 13. Sticky Provenance and Trust Inheritance

Provenance class must be sticky and dominant.

A clean hash of AI-generated content does not make that content human-authored.

Derived artifacts must inherit trust constraints from their lowest-trust ancestor.

Rules:

- AI-generated source remains AI-generated even when hashed.
- Summary of AI output remains derived from AI output.
- Human promotion can grant continuity authority, but it does not rewrite authorship.
- Trust class may be annotated upward by human judgment, but source class remains visible.

Do not launder dirty or low-trust content into apparent fact through clean fixity.

## 14. Redaction Without Deletion

Append-only preservation collides with legal and ethical erasure needs.

MiricleDrive requires tombstone redaction.

Tombstones should preserve:

- that content existed
- who redacted it
- why it was redacted
- when it was redacted
- what authority permitted redaction
- hash of redacted content if legally and ethically permissible
- scope of removal
- replacement access policy

The content may be removed or sealed.

The provenance of the removal remains.

## 15. Third-Party Content Scope

Always-on ingestion can create a surveillance archive of other people.

POV footage, messages, phone backups, and shared documents may include third parties who did not consent to permanent tamper-evident indexing.

MiricleDrive must support:

- third_party_detected
- consent_status
- restricted_visibility
- default_exclude policies
- family/minor sensitivity tiers
- legal hold
- redaction eligibility

Default ingest is not automatically default render.

## 16. Succession Primitive

A single human key is a single point of failure.

A continuity archive built to persist beyond one person cannot depend on one lost or deceased key.

MiricleDrive requires succession from the start.

Controls:

- threshold authority k-of-n
- designated successor roles
- heir promotion path
- emergency freeze path
- key rotation event
- key revocation event
- succession activation event
- recovery quorum

Succession events must themselves be signed and chained.

## 17. Authority Roles

Minimum authority roles:

- origin_authority
- successor_authority
- reviewer
- custodian
- technical_operator
- redaction_authority
- emergency_freeze_authority

Operators may run infrastructure.

Only authorized human roles may promote, redact, rotate keys, or change governance policy.

## 18. Protocol Events to Add

Required event types:

- ledger_anchor_created
- envelope_canonicalized
- envelope_hash_computed
- promotion_requested
- promotion_signed
- promotion_rejected
- review_queue_built
- review_threshold_changed
- review_deferred
- tombstone_created
- redaction_executed
- key_registered
- key_rotated
- key_revoked
- succession_rule_created
- succession_activated
- external_anchor_recorded

## 19. Next Schema Deltas

Add concrete schema support for:

1. cognition.envelope.schema.json
2. governance.event.schema.json
3. ledger.chain.schema.json
4. signed.promotion.schema.json
5. tombstone.redaction.schema.json
6. succession.authority.schema.json

These are the path from protocol-on-paper to protocol-in-the-file.

## 20. Final Principle

MiricleDrive cannot rely on the AI promising not to become the author.

It must make authorship capture structurally difficult, visible, and contestable.

Policy states the boundary.

Protocol enforces the boundary.

The next threshold is not better prose.

The next threshold is signed, chained, reviewable authority.
