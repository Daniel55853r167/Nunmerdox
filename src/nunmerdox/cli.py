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
import csv
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

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

app = typer.Typer(
    help="Nunmerdox - Scanner e OSINT de números telefónicos",
    rich_markup_mode="markdown"
)


def parse_phone_number(number: str) -> Optional[dict]:
    """
    Parsea un número telefónico usando phonenumbers.
    
    Retorna dict con: e164, country, intl
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


def print_menu(title: str, options: dict) -> int:
    """
    Muestra un menú numerado y retorna la opción seleccionada.
    
    Args:
        title: Título del menú
        options: Dict {número: descripción}
    
    Returns:
        Número de opción seleccionada
    """
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    
    for num, desc in sorted(options.items()):
        print(f"  {Colors.BOLD}{num}{Colors.ENDC}. {desc}")
    
    while True:
        try:
            choice = input(f"\n{Colors.GREEN}Selecciona opción: {Colors.ENDC}").strip()
            choice_int = int(choice)
            if choice_int in options:
                return choice_int
            else:
                print(f"{Colors.RED}Opción inválida. Intenta de nuevo.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.RED}Por favor ingresa un número.{Colors.ENDC}")


def interactive_mode():
    """Modo interactivo para ejecutar Nunmerdox sin argumentos CLI."""
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("""
    ███╗   ██╗██╗   ██╗███╗   ██╗███╗   ███╗███████╗██████╗ ██████╗  ██████╗ ██╗  ██╗
    ████╗  ██║██║   ██║████╗  ██║████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝
    ██╔██╗ ██║██║   ██║██╔██╗ ██║██╔████╔██║█████╗  ██████╔╝██║  ██║██║   ██║ ╚███╔╝ 
    ██║╚██╗██║██║   ██║██║╚██╗██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║  ██║██║   ██║ ██╔██╗ 
    ██║ ╚████║╚██████╔╝██║ ╚████║██║ ╚═╝ ██║███████╗██║  ██║██████╔╝╚██████╔╝██╔╝ ██╗
    ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
    """)
    print(f"{Colors.ENDC}")
    
    print(f"{Colors.YELLOW}⚠️  ADVERTENCIA LEGAL ⚠️{Colors.ENDC}")
    print("Este software es para pentesting, OSINT ético e investigación autorizada.")
    print("Uso no autorizado = responsabilidad legal del usuario.\n")
    
    # Sección 1: Entrada de números
    numbers = []
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}--- Agregar Números ---{Colors.ENDC}")
        print(f"Números ingresados: {Colors.GREEN}{len(numbers)}{Colors.ENDC}")
        
        if numbers:
            print(f"{Colors.CYAN}Lista actual:{Colors.ENDC}")
            for i, num in enumerate(numbers, 1):
                print(f"  {i}. {num}")
        
        options = {
            1: "Añadir un nuevo número",
            2: "Limpiar lista",
            3: "Continuar a opciones"
        }
        
        choice = print_menu("Gestión de números", options)
        
        if choice == 1:
            num = input(f"{Colors.GREEN}Ingresa número (ej: +34123456789 o 123456789): {Colors.ENDC}").strip()
            if num:
                numbers.append(num)
                print(f"{Colors.GREEN}✓ Número añadido{Colors.ENDC}")
            else:
                print(f"{Colors.RED}❌ Número vacío{Colors.ENDC}")
        elif choice == 2:
            numbers.clear()
            print(f"{Colors.YELLOW}✓ Lista limpiada{Colors.ENDC}")
        elif choice == 3:
            if numbers:
                break
            else:
                print(f"{Colors.RED}❌ Debes agregar al menos un número{Colors.ENDC}")
    
    # Sección 2: Configurar opciones
    osint_enabled = False
    osint_max = 5
    osint_delay = 1.0
    output_format = None
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}--- Configurar Opciones ---{Colors.ENDC}")
    
    while True:
        osint_status = '🟢 ACTIVADO' if osint_enabled else '🔴 DESACTIVADO'
        output_status = output_format or 'Consola (ninguno)'
        
        options = {
            1: f"OSINT: {osint_status}",
            2: f"Máx resultados OSINT: {Colors.YELLOW}{osint_max}{Colors.ENDC}",
            3: f"Delay entre queries: {Colors.YELLOW}{osint_delay}s{Colors.ENDC}",
            4: f"Formato salida: {Colors.YELLOW}{output_status}{Colors.ENDC}",
            5: "Comenzar escaneo"
        }
        
        choice = print_menu("Opciones de escaneo", options)
        
        if choice == 1:
            osint_enabled = not osint_enabled
            estado = "activado" if osint_enabled else "desactivado"
            print(f"{Colors.GREEN}✓ OSINT {estado}{Colors.ENDC}")
        
        elif choice == 2:
            try:
                val = int(input(f"{Colors.GREEN}Máx resultados (1-50): {Colors.ENDC}"))
                if 1 <= val <= 50:
                    osint_max = val
                    print(f"{Colors.GREEN}✓ Actualizado a {val}{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}❌ Debe estar entre 1 y 50{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}❌ Ingresa un número válido{Colors.ENDC}")
        
        elif choice == 3:
            try:
                val = float(input(f"{Colors.GREEN}Delay en segundos (0.1-5.0): {Colors.ENDC}"))
                if 0.1 <= val <= 5.0:
                    osint_delay = val
                    print(f"{Colors.GREEN}✓ Actualizado a {val}s{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}❌ Debe estar entre 0.1 y 5.0{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}❌ Ingresa un número válido{Colors.ENDC}")
        
        elif choice == 4:
            fmt_options = {
                1: "Consola (sin guardar)",
                2: "JSON",
                3: "TXT (texto legible)",
                4: "CSV"
            }
            fmt_choice = print_menu("Formato de salida", fmt_options)
            
            if fmt_choice == 1:
                output_format = None
            elif fmt_choice == 2:
                output_format = "resultados.json"
            elif fmt_choice == 3:
                output_format = "resultados.txt"
            elif fmt_choice == 4:
                output_format = "resultados.csv"
            
            if output_format:
                print(f"{Colors.GREEN}✓ Guardará en: {output_format}{Colors.ENDC}")
            else:
                print(f"{Colors.GREEN}✓ Mostrará en consola{Colors.ENDC}")
        
        elif choice == 5:
            break
    
    # Sección 3: Ejecutar
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Iniciando escaneo...{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    run_scan(numbers, osint_enabled, osint_max, osint_delay, output_format)


def run_scan(
    numbers: List[str],
    osint: bool = False,
    osint_max: int = 5,
    osint_delay: float = 1.0,
    output: Optional[str] = None
):
    """Ejecuta el escaneo con los parámetros dados."""
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
                    typer.echo(f"\n{Colors.CYAN}🔍 Ejecutando OSINT para {res['e164']}...{Colors.ENDC}")
                    osint_data = perform_osint(
                        res["e164"],
                        res.get("intl"),
                        max_results=osint_max,
                        delay=osint_delay
                    )
                    res["osint"] = osint_data
                    typer.echo(
                        f"   {Colors.GREEN}✓ {len(osint_data)} resultados encontrados{Colors.ENDC}"
                    )
                except Exception as e:
                    logger.exception(f"Error en OSINT para {res.get('e164')}")
                    res["osint_error"] = str(e)
            
            results.append(res)
    
    # Guardar resultados
    if output:
        save_results(results, output)
        typer.echo(f"\n{Colors.GREEN}✅ Resultados guardados en: {output}{Colors.ENDC}")
    else:
        # Mostrar en consola
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}RESULTADOS{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}")
        for res in results:
            print(json.dumps(res, indent=2, ensure_ascii=False))


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


@app.command()
def scan(
    numbers: Optional[List[str]] = typer.Argument(
        None,
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
    interactive: bool = typer.Option(
        False,
        "--interactive", "-i",
        help="Modo interactivo con menús"
    ),
):
    """
    Escanea números telefónicos y opcionalmente ejecuta búsquedas OSINT.
    
    **ADVERTENCIA LEGAL:**
    - Solo con consentimiento explícito para pentesting/OSINT ético
    - Respeta privacidad y legislación local
    - Las búsquedas son pasivas (indexadas públicamente)
    
    **Ejemplos:**
    
    Modo interactivo (recomendado):
    ```
    nunmerdox scan --interactive
    ```
    
    Escaneo rápido:
    ```
    nunmerdox scan "+34123456789" --agree-ethics --osint
    ```
    """
    
    # Si no hay números y no es interactivo, activar modo interactivo
    if not numbers and not interactive:
        interactive = True
    
    if interactive:
        interactive_mode()
        return
    
    if not agree_ethics:
        typer.echo(
            "❌ Debes usar --agree-ethics para confirmar uso legal y autorizado",
            err=True
        )
        raise typer.Exit(1)
    
    if osint and (osint_max < 1 or osint_delay < 0):
        typer.echo("❌ osint-max debe ser > 0 y osint-delay >= 0", err=True)
        raise typer.Exit(1)
    
    run_scan(numbers, osint, osint_max, osint_delay, output)


if __name__ == "__main__":
    app()
