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
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

logger = logging.getLogger(__name__)

# User-Agent para evitar bloqueos
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)


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
    ]
    
    # Dedupe preservando orden
    seen = set()
    out = []
    for item in q:
        if item not in seen:
            seen.add(item)
            out.append(item)
    
    return out


def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Busca en DuckDuckGo usando una simple solicitud HTTP.
    
    Args:
        query: Término de búsqueda
        max_results: Máximo de resultados a retornar
    
    Returns:
        Lista de resultados: {title, href, body}
    """
    results = []
    
    try:
        # URL de búsqueda de DuckDuckGo HTML
        url = "https://html.duckduckgo.com/"
        params = {"q": query}
        
        headers = {"User-Agent": USER_AGENT}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar resultados
        for result in soup.find_all('div', class_='result'):
            if len(results) >= max_results:
                break
            
            try:
                # Título y URL
                link = result.find('a', class_='result__url')
                if not link:
                    continue
                
                href = link.get('href', '')
                title_elem = result.find('a', class_='result__title')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # Snippet
                snippet_elem = result.find('a', class_='result__snippet')
                body = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                if href and title:
                    results.append({
                        "title": title,
                        "href": href,
                        "body": body
                    })
            except Exception as e:
                logger.debug(f"Error parsing resultado: {e}")
                continue
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error en búsqueda DuckDuckGo para '{query}': {e}")
    except Exception as e:
        logger.exception(f"Error inesperado en búsqueda: {e}")
    
    return results


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
            items = search_duckduckgo(q, max_results=max_results)
            if items:
                for it in items:
                    results.append({
                        "query": q,
                        **it
                    })
        except Exception as e:
            logger.exception(f"Error en búsqueda para query '{q}': {e}")
        
        time.sleep(delay)
    
    return results

