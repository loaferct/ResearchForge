"""Python bindings to the zero-dependency researchforge_core Rust library.

Provides high-performance, low-RAM implementations for text processing, quote verification,
passage search, paper deduplication, and lexical scoring.
"""

from __future__ import annotations

import ctypes
import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger("researchforge.rust")

_LIB: ctypes.CDLL | None = None


def _find_library() -> Path | None:
    pkg_dir = Path(__file__).parent
    workspace_root = pkg_dir.parent.parent

    candidates = [
        pkg_dir / "libresearchforge_core.so",
        pkg_dir / "researchforge_core.so",
        workspace_root / "crates" / "researchforge_core" / "target" / "release" / "libresearchforge_core.so",
        workspace_root / "crates" / "researchforge_core" / "target" / "debug" / "libresearchforge_core.so",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def _load_library() -> ctypes.CDLL | None:
    global _LIB
    if _LIB is not None:
        return _LIB

    lib_path = _find_library()
    if not lib_path:
        return None

    try:
        lib = ctypes.CDLL(str(lib_path))
        # Define argtypes and restype
        lib.rf_free_string.argtypes = [ctypes.c_void_p]
        lib.rf_free_string.restype = None

        lib.rf_normalize.argtypes = [ctypes.c_char_p]
        lib.rf_normalize.restype = ctypes.c_void_p

        lib.rf_quote_in.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.rf_quote_in.restype = ctypes.c_bool

        lib.rf_quote_in_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.rf_quote_in_file.restype = ctypes.c_bool

        lib.rf_abstract_overlap.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.rf_abstract_overlap.restype = ctypes.c_double

        lib.rf_title_fit.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.rf_title_fit.restype = ctypes.c_double

        lib.rf_title_name.argtypes = [ctypes.c_char_p]
        lib.rf_title_name.restype = ctypes.c_void_p

        lib.rf_title_key.argtypes = [ctypes.c_char_p]
        lib.rf_title_key.restype = ctypes.c_void_p

        lib.rf_relevance.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        lib.rf_relevance.restype = ctypes.c_double

        lib.rf_find_passages_json.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t]
        lib.rf_find_passages_json.restype = ctypes.c_void_p

        lib.rf_section_outline_json.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        lib.rf_section_outline_json.restype = ctypes.c_void_p

        lib.rf_query_terms_json.argtypes = [ctypes.c_char_p]
        lib.rf_query_terms_json.restype = ctypes.c_void_p

        _LIB = lib
        return lib
    except Exception as exc:
        log.warning("Failed to load Rust researchforge_core library: %s", exc)
        return None


def is_available() -> bool:
    return _load_library() is not None


def _consume_string(lib: ctypes.CDLL, ptr: int | None) -> str | None:
    if not ptr:
        return None
    try:
        val = ctypes.string_at(ptr).decode("utf-8", errors="replace")
        return val
    finally:
        lib.rf_free_string(ptr)


def normalize(text: str) -> str:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    text_bytes = text.encode("utf-8")
    ptr = lib.rf_normalize(text_bytes)
    res = _consume_string(lib, ptr)
    return res or ""


def quote_in(quote: str, haystack: str) -> bool:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    return bool(lib.rf_quote_in(quote.encode("utf-8"), haystack.encode("utf-8")))


def quote_in_file(quote: str, path: str | Path) -> bool:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    return bool(lib.rf_quote_in_file(quote.encode("utf-8"), str(path).encode("utf-8")))


def abstract_overlap(a: str, b: str) -> float:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    return float(lib.rf_abstract_overlap(a.encode("utf-8"), b.encode("utf-8")))


def title_fit(title: str, abstract: str) -> float:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    return float(lib.rf_title_fit(title.encode("utf-8"), abstract.encode("utf-8")))


def title_name(title: str) -> str | None:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    ptr = lib.rf_title_name(title.encode("utf-8"))
    return _consume_string(lib, ptr)


def title_key(title: str) -> str:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    ptr = lib.rf_title_key(title.encode("utf-8"))
    res = _consume_string(lib, ptr)
    return res or ""


def relevance(title: str, abstract: str, terms: list[str]) -> float:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    terms_json = json.dumps(terms)
    return float(lib.rf_relevance(title.encode("utf-8"), abstract.encode("utf-8"), terms_json.encode("utf-8")))


def find_passages(text: str, pattern: str, context: int = 300, limit: int = 8) -> list[dict[str, Any]]:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    ptr = lib.rf_find_passages_json(text.encode("utf-8"), pattern.encode("utf-8"), context, limit)
    res = _consume_string(lib, ptr)
    return json.loads(res or "[]")


def section_outline(text: str, limit: int = 40) -> list[dict[str, Any]]:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    ptr = lib.rf_section_outline_json(text.encode("utf-8"), limit)
    res = _consume_string(lib, ptr)
    return json.loads(res or "[]")


def query_terms(query: str) -> list[str]:
    lib = _load_library()
    if not lib:
        raise RuntimeError("Rust researchforge_core not available")
    ptr = lib.rf_query_terms_json(query.encode("utf-8"))
    res = _consume_string(lib, ptr)
    return json.loads(res or "[]")

