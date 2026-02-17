"""
CLI de Nunmerdox - Scanner e OSINT de números telefónicos.

ADVERTENCIA LEGAL:
- Este software está diseñado para pentesting, OSINT ético y ciberseguridad.
- Las búsquedas OSINT usan información públicamente indexada.
- Úsalo solo con autorización. El usuario es responsable del uso legal.
- No automatices scraping agresivo ni violes términos de servicio.
"""

import logging
import json
import sys
from typing import Optional, List
from pathlib import Path
import phonenumbers
import typer
from datetime import datetime

from .osint import perform_osint

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = typer.Typer(
    help="Nunmerdox - Scanner e OSINT de números telefónicos",
    rich_markup_mode="markdown"
)


def parse_phone_number(number: str) -> Optional[dict]:
    """
    Parsea un número telefónico usando phonenumbers.
    
    Retorna dict con: e164, country, operator, intl (si aplica)
    """
    try:
        # Intentar parsear con referencia por defecto (España)
        parsed = phonenumbers.parse(number, "ES")
        
        if not phonenumbers.is_valid_number(parsed):
            logger.warning(f"Número inválido: {number}")
            return None
        
        return {
            "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
            "intl": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "country": phonenumbers.region_code_for_number(parsed),
            "valid": True
        }
    except phonenumbers.phonenumberutil.NumberParseException as e:
        logger.error(f"Error al parsear {number}: {e}")
        return None


@app.command()
def scan(
    numbers: List[str] = typer.Argument(
        ...,
        help="Número o números a escanear (ej: +34123456789 o 123456789)"
    ),
    agree_ethics: bool = typer.Option(
        False,
        "--agree-ethics",
        help="Confirma que usarás este software legalmente"
    ),
    osint: bool = typer.Option(
        False,
        "--osint",
        help="Activar búsquedas OSINT (web, redes sociales, pastes)"
    ),
    osint_max: int = typer.Option(
        5,
        "--osint-max",
        help="Máx resultados por query OSINT (default 5)"
    ),
    osint_delay: float = typer.Option(
        1.0,
        "--osint-delay",
        help="Delay entre queries OSINT en segundos (default 1.0)"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Archivo de salida (JSON, TXT, CSV)"
    ),
):
    """
    Escanea números telefónicos y opcionalmente ejecuta búsquedas OSINT.
    
    **ADVERTENCIA LEGAL:**
    - Solo con consentimiento explícito para pentesting/OSINT ético
    - Respeta privacidad y legislación local
    - Las búsquedas son pasivas (indexadas públicamente)
    """
    
    if not agree_ethics:
        typer.echo(
            "❌ Debes usar --agree-ethics para confirmar uso legal y autorizado",
            err=True
        )
        raise typer.Exit(1)
    
    if osint and (osint_max < 1 or osint_delay < 0):
        typer.echo("❌ osint-max debe ser > 0 y osint-delay >= 0", err=True)
        raise typer.Exit(1)
    
    results = []
    
    with typer.progressbar(numbers, label="Escaneando números...") as progress:
        for number in progress:
            res = parse_phone_number(number)
            
            if not res:
                logger.warning(f"No se pudo procesar: {number}")
                continue
            
            # Ejecutar OSINT si está activado
            if osint:
                try:
                    typer.echo(f"🔍 Ejecutando OSINT para {res['e164']}...")
                    osint_data = perform_osint(
                        res["e164"],
                        res.get("intl"),
                        max_results=osint_max,
                        delay=osint_delay
                    )
                    res["osint"] = osint_data
                    typer.echo(
                        f"   ✓ {len(osint_data)} resultados encontrados"
                    )
                except Exception as e:
                    logger.exception(f"Error en OSINT para {res.get('e164')}")
                    res["osint_error"] = str(e)
            
            results.append(res)
    
    # Guardar resultados
    if output:
        save_results(results, output)
        typer.echo(f"✅ Resultados guardados en: {output}")
    else:
        # Mostrar en consola
        for res in results:
            typer.echo(json.dumps(res, indent=2, ensure_ascii=False))


def save_results(results: List[dict], filepath: str):
    """Guarda resultados en JSON, TXT o CSV según extensión."""
    path = Path(filepath)
    
    if path.suffix.lower() == ".json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    elif path.suffix.lower() == ".txt":
        with open(path, "w", encoding="utf-8") as f:
            for res in results:
                f.write(f"{'='*60}\n")
                f.write(f"Número: {res.get('e164', 'N/A')}\n")
                f.write(f"País: {res.get('country', 'N/A')}\n")
                f.write(f"Formato Intl: {res.get('intl', 'N/A')}\n")
                
                if res.get("osint"):
                    f.write(f"\nResultados OSINT ({len(res['osint'])} hallazgos):\n")
                    f.write("-" * 60 + "\n")
                    
                    for i, r in enumerate(res["osint"], 1):
                        f.write(f"\n{i}. Query: {r.get('query', 'N/A')}\n")
                        f.write(f"   Título: {r.get('title', 'N/A')}\n")
                        f.write(f"   URL: {r.get('href', 'N/A')}\n")
                        f.write(f"   Snippet: {r.get('body', 'N/A')}\n")
                
                if res.get("osint_error"):
                    f.write(f"\n⚠️ Error OSINT: {res['osint_error']}\n")
                
                f.write("\n")
    
    elif path.suffix.lower() == ".csv":
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "E164", "País", "Intl", "Query OSINT", "Título", "URL", "Snippet"
            ])
            
            for res in results:
                e164 = res.get("e164", "")
                pais = res.get("country", "")
                intl = res.get("intl", "")
                
                if res.get("osint"):
                    for r in res["osint"]:
                        writer.writerow([
                            e164, pais, intl,
                            r.get("query", ""),
                            r.get("title", ""),
                            r.get("href", ""),
                            r.get("body", "")
                        ])
                else:
                    writer.writerow([e164, pais, intl, "", "", "", ""])


if __name__ == "__main__":
    app()
