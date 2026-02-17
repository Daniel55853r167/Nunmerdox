# Nunmerdox - OSINT y análisis de números telefónicos

**Nunmerdox** es una herramienta CLI para escanear números telefónicos y ejecutar búsquedas OSINT pasivas en la web.

## Funcionalidades

- 📱 **Validación de números** usando librerías estándar de telefonía
- 🔍 **Búsquedas OSINT** automáticas en DuckDuckGo (webs, redes sociales, pastes)
- 📊 **Salida flexible** en JSON, TXT o CSV
- ⚡ **Control de límites** (máx resultados, delays entre queries)

## ⚠️ ADVERTENCIA LEGAL

**Este software está diseñado exclusivamente para:**
- Pentesting autorizado
- OSINT ético
- Investigación de ciberseguridad
- Casos legales y consentidos

**NO uses para:**
- Acoso, suplantación o fraude
- Scraping agresivo que viole TOS
- Automatización sin consentimiento
- Violación de privacidad

**El usuario es responsable del uso legal y autorizado.**

---

## Instalación

### En Kali Linux

```bash
git clone https://github.com/tu-usuario/Nunmerdox.git
cd Nunmerdox
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

### En Termux (Android)

```bash
apt update && apt upgrade -y
apt install python3 python3-pip git
git clone https://github.com/tu-usuario/Nunmerdox.git
cd Nunmerdox
pip install -r requirements.txt
pip install -e .
```

---

## Uso

### Escaneo simple

```bash
python -m nunmerdox scan "+34123456789" --agree-ethics
```

### Con búsquedas OSINT

```bash
python -m nunmerdox scan "+34123456789" --agree-ethics --osint
```

### Con opciones personalizadas

```bash
python -m nunmerdox scan "+34123456789" \
  --agree-ethics \
  --osint \
  --osint-max 7 \
  --osint-delay 1.5 \
  --output resultados.json
```

### Escanear múltiples números

```bash
python -m nunmerdox scan \
  "+34123456789" \
  "+34987654321" \
  "+351234567890" \
  --agree-ethics \
  --osint \
  -o resultados.csv
```

---

## Opciones CLI

| Opción | Descripción | Default |
|--------|-------------|---------|
| `--agree-ethics` | Confirma uso legal (obligatorio) | - |
| `--osint` | Activar búsquedas OSINT | False |
| `--osint-max N` | Máx resultados por query | 5 |
| `--osint-delay S` | Delay entre queries (seg) | 1.0 |
| `-o, --output FILE` | Archivo de salida | Consola |

---

## Salida

### JSON (recomendado)

```json
{
  "e164": "+34123456789",
  "intl": "+34 123 456 789",
  "country": "ES",
  "valid": true,
  "osint": [
    {
      "query": "\"+34123456789\"",
      "title": "Título del resultado",
      "href": "https://ejemplo.com/pagina",
      "body": "Snippet del contenido..."
    }
  ]
}
```

### TXT

```
============================================================
Número: +34123456789
País: ES
Formato Intl: +34 123 456 789

Resultados OSINT (5 hallazgos):
------------------------------------------------------------

1. Query: "+34123456789"
   Título: Resultado 1
   URL: https://...
   Snippet: ...
```

### CSV

| E164 | País | Intl | Query OSINT | Título | URL | Snippet |
|------|------|------|-------------|--------|-----|---------|

---

## Estructura del Proyecto

```
Nunmerdox/
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   └── nunmerdox/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py           # Interfaz de comandos
│       └── osint.py         # Motor OSINT
```

---

## Dependencias

- **phonenumbers** ≥8.13.0 - Parsing y validación de números
- **duckduckgo_search** ≥3.9.0 - Búsquedas OSINT
- **typer** ≥0.9.0 - CLI moderna

---

## Tips

1. **Ajusta los delays según tu conexión:**
   ```bash
   --osint-delay 2.0  # Para conexiones lentas
   --osint-delay 0.5  # Para conexiones rápidas
   ```

2. **Aumenta resultados para cobertura completa:**
   ```bash
   --osint-max 10  # Más exhaustivo
   ```

3. **Guarda resultados en diferentes formatos:**
   ```bash
   --output resultados.json  # Procesamiento automático
   --output resultados.txt   # Lectura humanizada
   --output resultados.csv   # Análisis en Excel
   ```

4. **Usa `&` para lanzar escaneos en background:**
   ```bash
   python -m nunmerdox scan ... --output out.json &
   ```

---

## Limitaciones y Notas

- DuckDuckGo puede aplicar rate limiting si haces muchas queries seguidas
- Algunos sitios bloquean búsquedas automáticas (respecta sus TOS)
- Los resultados varían según tu ubicación IP y configuración DNS
- Para cobertura máxima, combina con múltiples motores (ver desarrollo futuro)

---

## Desarrollo Futuro

- [ ] Soporte para múltiples motores (SerpAPI, Bing, Google Custom Search)
- [ ] Integración con APIs de verificación de carreras (HLR, LRN)
- [ ] Módulo de deduplicación y normalización
- [ ] Dashboard web interactivo
- [ ] Generación de reportes avanzados (PDF, HTML)
- [ ] Búsquedas en dark web (OnionSearch)

---

## Licencia

Este software se proporciona "tal cual" para propósitos de seguridad. El usuario asume toda responsabilidad por su uso.

---

## Contacto y Reportes

Para bugs, sugerencias o reportes de seguridad, abre un issue en GitHub.

**Recuerda: con gran poder viene gran responsabilidad. Úsalo ética y legalmente.**
