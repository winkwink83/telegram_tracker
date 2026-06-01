import json
from pathlib import Path


def load_last_update_id(state_file: Path) -> int:
    if not state_file.exists():
        return 0

    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        return int(data["last_update_id"])

    except Exception as exc:
        raise RuntimeError(
            f"Nie udało się wczytać state file: {state_file}"
        ) from exc


def save_last_update_id(state_file: Path, update_id: int) -> None:
    payload = {
        "last_update_id": update_id
    }

    state_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )