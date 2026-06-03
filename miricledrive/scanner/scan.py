#!/usr/bin/env python3
"""
MiricleDrive Scanner v0

Purpose:
Walk a source directory and emit witness-grade manifest records.

This does not summarize.
This does not interpret.
This does not delete.
This does not render a person.

It observes, hashes, timestamps, classifies, and records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import platform
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


SCHEMA_VERSION = "miricledrive.artifact_manifest.v1"


ARCHIVE_EXTENSIONS = {
    ".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz",
    ".tgz", ".tbz2", ".iso", ".dmg"
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".m4v", ".wmv", ".webm"
}

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".tiff", ".tif", ".bmp"
}

AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"
}

DOCUMENT_EXTENSIONS = {
    ".txt", ".md", ".pdf", ".doc", ".docx", ".rtf", ".odt",
    ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".json", ".xml", ".html"
}

AI_THREAD_HINTS = {
    "chatgpt", "claude", "gemini", "grok", "perplexity",
    "copilot", "deepseek", "openai", "anthropic"
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def iso_from_timestamp(ts: Optional[float]) -> Optional[str]:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> Optional[str]:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return None


def guess_artifact_type(path: Path) -> str:
    ext = path.suffix.lower()
    name = path.name.lower()
    full = str(path).lower()

    if ext in VIDEO_EXTENSIONS:
        return "video"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in ARCHIVE_EXTENSIONS:
        return "archive"
    if ext in DOCUMENT_EXTENSIONS:
        if any(hint in full for hint in AI_THREAD_HINTS):
            return "human_ai_thread"
        return "document"
    if any(hint in name for hint in AI_THREAD_HINTS):
        return "ai_conversation"
    if ext == ".log":
        return "log"

    return "unknown"


def guess_source_kind(path: Path) -> str:
    full = str(path).lower()

    if any(hint in full for hint in AI_THREAD_HINTS):
        return "ai_platform_export"
    if "gopro" in full or "dcim" in full:
        return "camera_card"
    if "icloud" in full or "google drive" in full or "onedrive" in full or "dropbox" in full:
        return "cloud_sync"
    if "github" in full:
        return "github_export"

    return "local_drive"


def guess_ai_thought(path: Path, artifact_type: str) -> Dict[str, Any]:
    full = str(path).lower()

    ai_artifact_types = {
        "ai_conversation",
        "prompt",
        "ai_response",
        "human_ai_thread",
        "thought_trace",
        "reasoning_export",
        "correction_event",
        "model_comparison",
        "research_note",
    }

    is_ai = artifact_type in ai_artifact_types or any(hint in full for hint in AI_THREAD_HINTS)

    platform_guess = None
    for hint in AI_THREAD_HINTS:
        if hint in full:
            platform_guess = hint
            break

    return {
        "is_ai_augmented_thought": is_ai,
        "conversation_id": None,
        "thread_id": None,
        "turn_index": None,
        "speaker_role": "unknown",
        "platform": platform_guess,
        "model_name": None,
        "model_provider": None,
        "prompt_hash": None,
        "response_hash": None,
        "contains_human_original_text": None,
        "contains_ai_generated_text": None,
        "contains_tool_output": None,
        "contains_correction": None,
        "correction_target_record_id": None,
        "thought_artifact_class": "thread_export" if is_ai else "unknown",
        "authorship_boundary": "unknown",
        "rendering_constraint": "human_review_required" if is_ai else "unknown",
    }


def read_stat(path: Path) -> Dict[str, Any]:
    st = path.stat()
    return {
        "byte_size": st.st_size,
        "observed_ctime": iso_from_timestamp(getattr(st, "st_ctime", None)),
        "observed_mtime": iso_from_timestamp(getattr(st, "st_mtime", None)),
        "observed_atime": iso_from_timestamp(getattr(st, "st_atime", None)),
    }


def build_record(path: Path, root: Path, scanner_run_id: str, source_label: Optional[str]) -> Dict[str, Any]:
    record_id = str(uuid.uuid4())
    relative_path = str(path.relative_to(root)) if path != root else path.name
    ext = path.suffix.lower() if path.suffix else None
    mime_type, _ = mimetypes.guess_type(str(path))
    ingested_at = utc_now()

    try:
        stat = read_stat(path)
        read_status = "readable"
        corruption_status = "unknown"
        error_message = None
    except Exception as exc:
        stat = {
            "byte_size": 0,
            "observed_ctime": None,
            "observed_mtime": None,
            "observed_atime": None,
        }
        read_status = "unreadable"
        corruption_status = "unreadable"
        error_message = repr(exc)

    file_hash = sha256_file(path) if path.is_file() and read_status == "readable" else None

    if path.is_dir():
        record_type = "directory_marker"
        artifact_type = "directory"
    else:
        record_type = "filesystem_file"
        artifact_type = guess_artifact_type(path)

    source_kind = guess_source_kind(path)
    ai_thought = guess_ai_thought(path, artifact_type)

    is_archive = ext in ARCHIVE_EXTENSIONS if ext else False

    record = {
        "manifest_version": SCHEMA_VERSION,
        "scanner_run_id": scanner_run_id,
        "record_id": record_id,
        "record_type": record_type,
        "artifact_type": artifact_type,
        "preservation_class": "original_candidate",
        "path": str(path),
        "normalized_path": relative_path.replace("\\", "/"),
        "parent_path": str(path.parent),
        "file_name": path.name,
        "extension": ext,
        "mime_type_guess": mime_type,
        "byte_size": stat["byte_size"],
        "hashes": {
            "sha256": file_hash,
            "blake3": None,
            "md5_legacy": None,
        },
        "timestamps": {
            "observed_ctime": stat["observed_ctime"],
            "observed_mtime": stat["observed_mtime"],
            "observed_atime": stat["observed_atime"],
            "exif_capture_time": None,
            "media_created_time": None,
            "conversation_created_time": None,
            "conversation_updated_time": None,
            "filename_time_guess": None,
            "ingested_at": ingested_at,
            "timezone_context": "UTC",
            "time_confidence": "medium" if stat["observed_mtime"] else "unknown",
            "time_notes": "Filesystem timestamp only. Not proof of original capture time.",
        },
        "provenance": {
            "source_kind": source_kind,
            "source_label": source_label,
            "source_platform": ai_thought["platform"],
            "source_model": None,
            "source_device_id": platform.node(),
            "source_volume_id": None,
            "source_archive_record_id": None,
            "archive_internal_path": None,
            "observed_original_path": str(path),
            "source_confidence": "medium",
            "chain_of_custody_notes": "Observed by MiricleDrive scanner. No interpretation performed.",
        },
        "ai_thought": ai_thought,
        "archive": {
            "is_archive": is_archive,
            "archive_format": ext[1:] if is_archive and ext else None,
            "member_count": None,
            "extraction_status": "not_attempted" if is_archive else "not_applicable",
            "parent_archive_record_id": None,
            "nested_depth": None,
        },
        "media": {
            "duration_seconds": None,
            "width": None,
            "height": None,
            "frame_rate": None,
            "codec": None,
            "audio_present": None,
            "video_present": None,
        },
        "status": {
            "read_status": read_status,
            "corruption_status": corruption_status,
            "format_risk_level": "unknown",
            "error_message": error_message,
        },
        "duplicate_tracking": {
            "exact_duplicate_group_id": None,
            "near_duplicate_group_id": None,
            "duplicate_role": "unknown",
        },
        "governance": {
            "access_restriction": "unknown",
            "privacy_sensitivity": "unknown",
            "human_review_priority": "unknown",
            "ai_authorship_risk": "high" if ai_thought["is_ai_augmented_thought"] else "unknown",
        },
        "evidence_level": "recorded",
        "notes": None,
    }

    return record


def iter_paths(root: Path, include_dirs: bool = False) -> Iterable[Path]:
    for current_root, _dirs, files in os.walk(root):
        current = Path(current_root)

        if include_dirs:
            yield current

        for name in files:
            yield current / name


def write_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            f.write("\n")
            count += 1
    return count


def build_duplicates(manifest_path: Path, output_path: Path) -> Dict[str, Any]:
    groups: Dict[str, list] = {}

    with manifest_path.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            sha = record.get("hashes", {}).get("sha256")
            if sha:
                groups.setdefault(sha, []).append({
                    "record_id": record["record_id"],
                    "path": record["path"],
                    "byte_size": record["byte_size"],
                })

    duplicate_groups = {sha: items for sha, items in groups.items() if len(items) > 1}

    payload = {
        "generated_at": utc_now(),
        "exact_duplicate_group_count": len(duplicate_groups),
        "exact_duplicate_groups": duplicate_groups,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, sort_keys=True)

    return payload


def build_fixity_baseline(manifest_path: Path, output_path: Path) -> int:
    count = 0
    with manifest_path.open("r", encoding="utf-8") as src, output_path.open("w", encoding="utf-8") as out:
        for line in src:
            record = json.loads(line)
            sha = record.get("hashes", {}).get("sha256")
            if sha:
                out.write(f"{sha}  {record['normalized_path']}\n")
                count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="MiricleDrive witness-grade ingestion scanner v0.")
    parser.add_argument("source", help="Source folder to scan.")
    parser.add_argument("--output", default="miricledrive_scan_output", help="Output folder.")
    parser.add_argument("--source-label", default=None, help="Human-readable source label.")
    parser.add_argument("--include-dirs", action="store_true", help="Include directory marker records.")
    args = parser.parse_args()

    root = Path(args.source).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not root.exists():
        print(f"Source does not exist: {root}", file=sys.stderr)
        return 2

    scanner_run_id = str(uuid.uuid4())

    manifest_path = output_dir / "manifest.ndjson"
    duplicates_path = output_dir / "duplicates.json"
    fixity_path = output_dir / "fixity-baseline.txt"
    ingest_events_path = output_dir / "ingest-events.ndjson"

    def records() -> Iterable[Dict[str, Any]]:
        for path in iter_paths(root, include_dirs=args.include_dirs):
            yield build_record(path, root, scanner_run_id, args.source_label)

    manifest_count = write_jsonl(manifest_path, records())
    duplicate_payload = build_duplicates(manifest_path, duplicates_path)
    fixity_count = build_fixity_baseline(manifest_path, fixity_path)

    ingest_event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "scan_completed",
        "scanner_run_id": scanner_run_id,
        "source": str(root),
        "source_label": args.source_label,
        "started_or_recorded_at": utc_now(),
        "manifest_path": str(manifest_path),
        "duplicates_path": str(duplicates_path),
        "fixity_baseline_path": str(fixity_path),
        "manifest_record_count": manifest_count,
        "fixity_record_count": fixity_count,
        "exact_duplicate_group_count": duplicate_payload["exact_duplicate_group_count"],
        "host": platform.node(),
        "platform": platform.platform(),
        "non_invention_boundary": "Scanner observed files and metadata only. No semantic interpretation performed.",
    }

    with ingest_events_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(ingest_event, indent=2, ensure_ascii=False, sort_keys=True))
        f.write("\n")

    print("MiricleDrive scan complete.")
    print(f"Scanner run: {scanner_run_id}")
    print(f"Manifest records: {manifest_count}")
    print(f"Fixity records: {fixity_count}")
    print(f"Duplicate groups: {duplicate_payload['exact_duplicate_group_count']}")
    print(f"Output: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
