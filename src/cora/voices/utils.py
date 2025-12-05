from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Optional, Tuple


VoiceEntry = Tuple[str, str]


def _find_duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)
    return duplicates


def validate_voice_entries(entries: Iterable[VoiceEntry]) -> List[VoiceEntry]:
    entries_list = list(entries)
    name_duplicates = _find_duplicates(name for name, _ in entries_list)
    id_duplicates = _find_duplicates(voice_id for _, voice_id in entries_list)
    if name_duplicates or id_duplicates:
        problems = []
        if name_duplicates:
            problems.append(f"names: {', '.join(sorted(name_duplicates))}")
        if id_duplicates:
            problems.append(f"voice_ids: {', '.join(sorted(id_duplicates))}")
        raise ValueError(f"Duplicate voice entries detected ({'; '.join(problems)})")
    return entries_list


def combine_voice_entries(
    default_entries: Iterable[VoiceEntry],
    additions: Optional[Mapping[str, str]] = None,
) -> List[VoiceEntry]:
    combined: List[VoiceEntry] = list(default_entries)
    if additions:
        combined.extend(additions.items())
    return validate_voice_entries(combined)


def merge_voice_maps(
    *,
    defaults: Mapping[str, str],
    additions: Optional[Mapping[str, str]],
) -> Dict[str, str]:
    combined_entries = combine_voice_entries(defaults.items(), additions)
    return {name: voice_id for name, voice_id in combined_entries}

