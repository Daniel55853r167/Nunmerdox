"""Entry point para ejecutar Nunmerdox como módulo."""

import sys
from .cli import print_menu, quick_mode, interactive_mode

def main_menu():
    """Menú principal de Nunmerdox."""
    
    print(f"\n{'='*60}")
    print("NUNMERDOX - OSINT Scanner de Números Telefónicos")
    print(f"{'='*60}\n")
    
    options = {
        1: "OSINT Completo (con opciones)",
        2: "OSINT Rápido (solo número)"
    }
    
    choice = print_menu("Selecciona modo", options)
    
    if choice == 1:
        interactive_mode()
    elif choice == 2:
        quick_mode()

if __name__ == "__main__":
    main_menu()

