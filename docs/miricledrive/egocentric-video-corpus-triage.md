# MiricleDrive: Egocentric Video Corpus Triage

## POV Capture Doctrine and Multimodal Continuity Handling

Status: Working doctrine  
Purpose: Define how MiricleDrive should handle first-person POV video, chest-mounted footage, wearable capture, and high-volume daily-life recordings.

## 1. Core Claim

First-person video is the highest-fidelity primary signal in the archive, but it is also the heaviest.

It captures voice, gaze direction, gesture, decisions in context, relationships, movement through space, environmental cues, and daily operating reality.

That makes it multimodal coherence gold.

It also creates the fastest path to storage overload.

The capture instinct is correct. The open problem is triage.

## 2. Classification

MiricleDrive classifies continuous POV video as primary physical memory in artifact form.

It is not automatically refined continuity.

It is not automatically noise.

It is high-density continuity ore that requires provenance, segmentation, indexing, and load-bearing detection before compression or rendering.

## 3. First Law of POV Processing

Do not summarize the footage first.

Inventory it first.

The lawful first pass is:

- preserve original files
- hash each file
- extract technical metadata
- preserve folder and card structure
- map capture device and mount type when known
- extract timestamps
- detect clock drift
- create low-resolution proxy copies for review
- segment by file boundary and time interval
- mark corruption or missing audio
- keep original footage untouched

## 4. Raw Master vs. Proxy

Every POV file should be treated as two different things:

1. Raw master: original video file, untouched, hash-verified, never edited.
2. Proxy view: smaller review file, generated for indexing, transcription, visual scanning, and retrieval.

The proxy may be compressed.

The raw master remains source.

No proxy may replace the raw master.

## 5. Minimum Metadata Envelope

Each POV recording should receive a metadata envelope:

- File ID
- Raw hash
- File path
- File size
- Device model if known
- Mount type if known
- Capture start time
- Capture end time
- Timestamp confidence
- Location if available
- Audio present or absent
- Video present or corrupted
- File duration
- Resolution
- Frame rate
- Codec
- Source card or drive if known
- Ingest date
- Related archive event
- Privacy sensitivity tier
- Human review priority

Unknown fields remain unknown.

Do not infer beyond evidence.

## 6. Triage Problem

Continuous POV footage contains both high-signal and low-signal periods.

High-signal examples:

- family interaction
- conflict
- apology
- teaching
- work decision
- faith practice
- creative dictation
- self-correction
- project breakthrough
- health event
- grief anchor
- major purchase or transition
- conversation that changes later behavior

Low-signal examples:

- long drives with no meaningful speech
- routine errands
- setup time
- camera adjustment
- duplicate tests
- empty rooms
- accidental recordings
- background-only footage

Low-signal does not mean worthless.

It means lower review priority.

## 7. Load-Bearing Detection

MiricleDrive should detect candidate load-bearing segments using observable signals, not narrative guesswork.

Candidate signals:

- speech density
- named people appearing
- repeated project terms
- emotional language stated explicitly
- decision phrases such as "I decided," "we need to," or "I was wrong"
- conflict markers
- correction events
- unusual location or time
- strong later reference in other archive material
- relationship centrality
- long-term recurrence of the topic

The system may flag candidates.

The system may not declare final meaning without human review.

## 8. Segmentation Classes

POV footage should be segmented into reviewable units:

- Raw File Segment: the original recording file boundary.
- Time Slice Segment: fixed interval, such as 5 or 10 minutes.
- Speech Segment: bounded by detected speech or conversation.
- Event Segment: bounded by change in location, participant, or activity.
- Load-Bearing Candidate: segment flagged for review.
- Witness Capsule Candidate: segment likely worth curated preservation with notes and citations.

Segments are pointers.

Segments are not replacements for raw footage.

## 9. Compression Rule

Do not compress meaning before preserving source.

Allowed compression:

- proxy video generation
- transcript extraction
- keyframe extraction
- scene boundary detection
- topic indexing
- audio waveform index
- face or person candidate indexing with privacy controls
- event timeline pointers

Forbidden compression:

- deleting raw footage because proxy exists
- converting lived footage into a single summary
- smoothing contradictions
- generating scenes that were not recorded
- filling gaps between recordings
- presenting inferred emotion as fact
- producing a first-person synthetic narrator from the footage

## 10. Capture Going Forward

Future capture should improve metadata at the moment of recording.

Recommended capture habits:

- record date and device consistently
- preserve original card structure before copying
- avoid renaming raw files destructively
- keep battery or card changes as natural archive boundaries
- create a short spoken marker when recording begins, when appropriate
- tag major capture days in a simple ledger
- separate test footage from intentional capture
- keep private or sensitive footage in a restricted tier

The goal is not to record everything forever.

The goal is to preserve encounterable memory with enough provenance to remain trustworthy.

## 11. Privacy and Human Boundary

POV video captures other people as well as the wearer.

Therefore it requires stricter governance than ordinary documents.

MiricleDrive should support:

- privacy sensitivity tiers
- restricted family material
- third-party appearance flags
- legal or workplace caution flags
- posthumous access rules
- human veto authority
- no public rendering by default

The presence of a person in footage does not grant the AI authority to interpret that person.

The AI may identify, index, and retrieve.

It may not invent intent, emotion, consent, or meaning.

## 12. End State

The goal of POV video processing is not to make a life movie.

The goal is to create a witness-grade index over lived signal.

A future query should be able to ask:

- Show the original footage from this day.
- Show every segment where this project was discussed.
- Show all correction events captured on video.
- Show family interactions from this period with raw source links.
- Show what happened before and after this decision.
- Show segments with high speech density and known participants.

The answer must be evidence first.

No synthetic life story.

No counterfeit continuity.

## 13. Core Axioms

First-person video is primary physical memory.

The raw master is sacred source.

The proxy is a tool.

Inventory before interpretation.

Segment before summary.

Flag before judging.

Compression must preserve source linkage.

Continuous capture creates memory gravity.

The witness sorts, but the human decides meaning.
