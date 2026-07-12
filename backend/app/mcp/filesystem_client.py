from pathlib import Path

from langchain_core.tools import BaseTool, tool

from app.utils.config import get_settings


def _resolve(rel_path: str) -> Path:
    root = Path(get_settings().filesystem_root).resolve()
    target = (root / rel_path).resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"Path escapes filesystem root: {rel_path}")
    return target


@tool
def fs_list_dir(path: str = ".") -> list[str]:
    """List entries in a directory relative to the configured filesystem root."""
    target = _resolve(path)
    if not target.is_dir():
        raise ValueError(f"Not a directory: {path}")
    return [p.name + ("/" if p.is_dir() else "") for p in sorted(target.iterdir())]


@tool
def fs_read_file(path: str, max_bytes: int = 20000) -> str:
    """Read a UTF-8 text file relative to the configured filesystem root."""
    target = _resolve(path)
    if not target.is_file():
        raise ValueError(f"Not a file: {path}")
    return target.read_text(encoding="utf-8", errors="replace")[:max_bytes]


def get_filesystem_tools() -> list[BaseTool]:
    if not get_settings().filesystem_root:
        return []
    return [fs_list_dir, fs_read_file]
