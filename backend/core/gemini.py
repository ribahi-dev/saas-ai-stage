"""Configuration centralisee Gemini (cle API, nom de modele)."""

from __future__ import annotations

import os


def gemini_api_key() -> str | None:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    return key or None


def gemini_model_name() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-1.5-flash").strip() or "gemini-1.5-flash"


def configure_gemini_client() -> bool:
    """
    Configure le client google.generativeai.
    Retourne False si pas de cle (l'appelant doit utiliser un fallback).
    """
    api_key = gemini_api_key()
    if not api_key:
        return False
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    return True
