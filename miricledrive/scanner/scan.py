#!/usr/bin/env python3
"""
MiricleDrive Scanner v1

Purpose:
Witness-grade ingestion and fixity baseline generation.

This scanner is a preservation kernel, not a reasoning engine.
It observes files, computes SHA-256 fixity, records events, separates observed data from derived guesses, and emits audit outputs.

It does not summarize.
It does not interpret meaning.
It does not delete.
It does not render a person.
It does not fill gaps.
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
from typing import Any, Dict, Iterable, Optional, Tuple


SCHEMA_VERSION = "miricledrive.artifact_manifest.v1.1"

ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".rar", ".7z", ".tgz", ".bz2", ".xz", ".iso", ".dmg"}
AI_THREAD_HINTS = {"chatgpt", "claude", "gemini", "grok", "perplexity", "copilot", "deepseek", "openai", "anthropic"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def iso_from_timestamp(timestamp: Optional[float]) -> Optional[str]:
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


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


def has_ai_thread_hint(path: Path) -> bool:
    full = str(path).lower()
    return any(hint in full for hint in AI_THREAD_HINTS)


def guess_artifact_type(path: Path) -> str:
    ext = path.suffix.lower()
    full = str(path).lower()

    if ext in {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".wmv", ".webm"}:
        return "video"
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".tiff", ".tif", ".bmp"}:
        return "image"
    if ext in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"}:
        return "audio"
    if ext in ARCHIVE_EXTENSIONS:
        return "archive"
    if ext in {".txt", ".md", ".json", ".html", ".xml"} and has_ai_thread_hint(path):
        return "human_ai_thread"
    if ext in {".txt", ".md", ".pdf", ".doc", ".docx", ".rtf", ".odt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".json", ".xml", ".html"}:
        return "document"
    if "github" in full:
        return "code_commit"
    if ext == ".log":
        return "log"
    return "unknown"


def guess_source_kind(path: Path) -> str:
    full = str(path).lower()
    if has_ai_thread_hint(path):
        return "ai_platform_export"
    if "gopro" in full or "dcim" in full:
        return "camera_card"
    if "icloud" in full or "google drive" in full or "onedrive" in full or "dropbox" in full:
        return "cloud_sync"
    if "github" in full:
        return "github_export"
    return "local_drive"


def build_error(path: Path, scanner_run_id: str, error_type: str, exc: Exception | str) -> Dict[str, Any]:
    return {
        "error_id": str(uuid.uuid4()),
        "scanner_run_id": scanner_run_id,
        "path": str(path),
        "error_type": error_type,
        "error_message": repr(exc),
        "timestamp": utc_now(),
    }


def build_record(path: Path, root: Path, scanner_run_id: str, source_label: Optional[str]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    record_id = str(uuid.uuid4())
    relative_path = str(path.relative_to(root)) if path != root else path.name

    try:
        st = path.stat()
    except Exception as exc:
        return None, build_error(path, scanner_run_id, "stat_failure", exc)

    byte_size = st.st_size
    ext = path.suffix.lower() if path.suffix else None
    observed_mtime = iso_from_timestamp(getattr(st, "st_mtime", None))
    observed_ctime = iso_from_timestamp(getattr(st, "st_ctime", None))
    observed_atime = iso_from_timestamp(getattr(st, "st_atime", None))

    file_hash = None
    if path.is_file():
        file_hash = sha256_file(path)
        if not file_hash:
            return None, build_error(path, scanner_run_id, "read_failure", "Failed to generate SHA-256 hash")

    artifact_type_guess = guess_artifact_type(path)
    source_kind_guess = guess_source_kind(path)
    mime_type_guess = mimetypes.guess_type(str(path))[0]
    ai_thread_hint = has_ai_thread_hint(path)
    is_archive_guess = ext in ARCHIVE_EXTENSIONS if ext else False

    record = {
        "manifest_version": SCHEMA_VERSION,
        "scanner_run_id": scanner_run_id,
        "record_id": record_id,
        "record_type": "directory_marker" if path.is_dir() else "filesystem_file",
        "observed_data": {
            "path": str(path),
            "normalized_path": relative_path.replace("\\", "/"),
            "parent_path": str(path.parent),
            "file_name": path.name,
            "extension": ext,
            "byte_size": byte_size,
            "hashes": {
                "sha256": file_hash,
                "blake3": None
            },
            "timestamps": {
                "observed_ctime": observed_ctime,
                "observed_mtime": observed_mtime,
                "observed_atime": observed_atime,
                "ingested_at": utc_now()
            }
        },
        "derived_data": {
            "mime_type_guess": mime_type_guess,
            "artifact_type_guess": artifact_type_guess,
            "source_kind_guess": source_kind_guess,
            "is_archive_guess": is_archive_guess,
            "ai_thread_hint": ai_thread_hint,
            "time_confidence": "medium" if observed_mtime else "unknown",
            "time_notes": "Filesystem timestamp only. Not proof of original capture or creation time."
        },
        "governance": {
            "evidence_level": "recorded",
            "access_restriction": "unknown",
            "privacy_sensitivity": "unknown",
            "human_review_priority": "unknown",
            "ai_authorship_risk": "high" if ai_thread_hint else "unknown",
            "non_invention_boundary": "Observed data is separated from derived guesses. No semantic interpretation performed."
        },
        "status": {
            "read_status": "readable",
            "corruption_status": "unknown",
            "format_risk_level": "unknown"
        },
        "provenance": {
            "source_label": source_label,
            "source_device_id": platform.node(),
            "observed_original_path": str(path),
            "source_confidence": "medium",
            "chain_of_custody_notes": "Observed by MiricleDrive scanner. No interpretation performed."
        }
    }

    return record, None


def write_event(events_path: Path, event: Dict[str, Any]) -> None:
    with events_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True))
        f.write("\n")


def iter_file_paths(root: Path) -> Iterable[Path]:
    for current_root, _dirs, files in os.walk(root):
        for name in files:
            yield Path(current_root) / name


def build_duplicates(manifest_path: Path, output_path: Path) -> Dict[str, Any]:
    groups: Dict[str, list] = {}

    with manifest_path.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            sha = record.get("observed_data", {}).get("hashes", {}).get("sha256")
            if sha:
                groups.setdefault(sha, []).append({
                    "record_id": record["record_id"],
                    "path": record["observed_data"]["path"],
                    "byte_size": record["observed_data"]["byte_size"],
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
            sha = record.get("observed_data", {}).get("hashes", {}).get("sha256")
            normalized_path = record.get("observed_data", {}).get("normalized_path")
            if sha and normalized_path:
                out.write(f"{sha}  {normalized_path}\n")
                count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="MiricleDrive witness-grade ingestion scanner v1.")
    parser.add_argument("source", help="Source folder to scan.")
    parser.add_argument("--output", default="miricledrive_scan_output", help="Output folder.")
    parser.add_argument("--source-label", default=None, help="Human-readable source label.")
    parser.add_argument("--write-blocker-active", action="store_true", help="Indicates original media is protected by a write blocker or read-only policy.")
    args = parser.parse_args()

    root = Path(args.source).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not root.exists():
        print(f"Source does not exist: {root}", file=sys.stderr)
        return 2

    scanner_run_id = str(uuid.uuid4())
    start_time = utc_now()

    manifest_path = output_dir / "manifest.ndjson"
    errors_path = output_dir / "errors.ndjson"
    duplicates_path = output_dir / "duplicates.json"
    events_path = output_dir / "ingest-events.ndjson"
    fixity_path = output_dir / "fixity-baseline.txt"

    write_event(events_path, {
        "event_id": str(uuid.uuid4()),
        "event_type": "scan_started",
        "scanner_run_id": scanner_run_id,
        "timestamp": start_time,
        "source": str(root),
        "source_label": args.source_label,
        "write_blocker_active": bool(args.write_blocker_active),
        "host": platform.node(),
        "platform": platform.platform(),
        "non_invention_boundary": "Scanner observes files and metadata only. No semantic interpretation performed."
    })

    manifest_count = 0
    error_count = 0

    with manifest_path.open("w", encoding="utf-8") as mf, errors_path.open("w", encoding="utf-8") as ef:
        for path in iter_file_paths(root):
            record, error = build_record(path, root, scanner_run_id, args.source_label)
            if error:
                ef.write(json.dumps(error, ensure_ascii=False, sort_keys=True))
                ef.write("\n")
                error_count += 1
                continue
            if record:
                mf.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
                mf.write("\n")
                manifest_count += 1

    duplicate_payload = build_duplicates(manifest_path, duplicates_path)
    fixity_count = build_fixity_baseline(manifest_path, fixity_path)
    end_time = utc_now()

    write_event(events_path, {
        "event_id": str(uuid.uuid4()),
        "event_type": "scan_completed",
        "scanner_run_id": scanner_run_id,
        "timestamp": end_time,
        "source": str(root),
        "source_label": args.source_label,
        "manifest_path": str(manifest_path),
        "duplicates_path": str(duplicates_path),
        "errors_path": str(errors_path),
        "fixity_baseline_path": str(fixity_path),
        "manifest_record_count": manifest_count,
        "error_count": error_count,
        "fixity_record_count": fixity_count,
        "exact_duplicate_group_count": duplicate_payload["exact_duplicate_group_count"],
        "write_blocker_active": bool(args.write_blocker_active),
        "host": platform.node(),
        "platform": platform.platform(),
        "non_invention_boundary": "Scan completed without semantic interpretation."
    })

    print("MiricleDrive scan complete.")
    print(f"Scanner run: {scanner_run_id}")
    print(f"Manifest records: {manifest_count}")
    print(f"Errors: {error_count}")
    print(f"Fixity records: {fixity_count}")
    print(f"Duplicate groups: {duplicate_payload['exact_duplicate_group_count']}")
    print(f"Output: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
