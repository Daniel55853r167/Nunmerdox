"""
Módulo OSINT para Nunmerdox.
Realiza búsquedas pasivas en DuckDuckGo para encontrar menciones de números en web.

ADVERTENCIA LEGAL:
- Este módulo realiza búsquedas sobre información públicamente indexada.
- Úsalo solo con autorización para fines de pentesting, OSINT ético y ciberseguridad.
- No automatices explotación, scraping agresivo ni violes TOS de servicios terceros.
- El usuario es responsable de uso legal y autorizado.
"""

from typing import List, Dict, Any, Optional
import time
import logging
from duckduckgo_search import ddg

logger = logging.getLogger(__name__)


def build_osint_queries(e164: str, intl: Optional[str] = None) -> List[str]:
    """
    Construye una lista de queries OSINT para buscar un número en la web.
    
    Args:
        e164: Número en formato E.164 (ej: +34123456789)
        intl: Número en formato internacional legible (ej: +34 123 456 789)
    
    Returns:
        Lista de queries deduplicadas ordenadas.
    """
    q = []
    
    # Query base exacta
    q.append(f'"{e164}"')
    
    if intl:
        q.append(f'"{intl}"')
    
    # Redes sociales y sitios comunes
    q += [
        f'{e164} facebook',
        f'{e164} twitter',
        f'{e164} instagram',
        f'{e164} whatsapp',
        f'{e164} "contacto"',
        f'{e164} "teléfono"',
        f'{e164} site:pastebin.com',
        f'{e164} site:reddit.com',
        f'{e164} site:linkedin.com',
        f'{e164} site:disqus.com',
    ]
    
    # Dedupe preservando orden
    seen = set()
    out = []
    for item in q:
        if item not in seen:
            seen.add(item)
            out.append(item)
    
    return out


def perform_osint(
    e164: str,
    intl: Optional[str] = None,
    max_results: int = 5,
    delay: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Ejecuta búsquedas DuckDuckGo para una lista de queries relacionadas con el número.
    
    Args:
        e164: Número E.164
        intl: Número formato internacional
        max_results: Máximo número de resultados por query
        delay: Delay en segundos entre queries
    
    Returns:
        Lista de dicts con keys: query, title, href, body
    """
    queries = build_osint_queries(e164, intl)
    results: List[Dict[str, Any]] = []
    
    for q in queries:
        try:
            items = ddg(q, max_results=max_results)
            if items:
                for it in items:
                    results.append({
                        "query": q,
                        "title": it.get("title"),
                        "href": it.get("href"),
                        "body": it.get("body")
                    })
        except Exception as e:
            logger.exception("Error en ddg para query '%s': %s", q, e)
        
        time.sleep(delay)
    
    return results
