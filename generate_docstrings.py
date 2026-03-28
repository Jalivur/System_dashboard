#!/usr/bin/env python3
"""
generate_docstrings.py — Generador/regenerador de docstrings via Groq
Uso: python3 generate_docstrings.py /ruta/al/proyecto [--dry-run] [--file ruta.py]
Requiere: pip install groq
API key: variable de entorno GROQ_API_KEY o argumento --api-key
"""

import ast
import sys
import os
import argparse
import textwrap
import time
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    print("❌ Instala el cliente: pip install groq")
    sys.exit(1)

# ── Configuración ─────────────────────────────────────────────────────────────

LAYERS = [
    "core/",
    "ui/",
    "ui/windows/",
    "config/",
    "utils/",
]

# Modelo Groq — llama-3.3-70b es el más capaz en tier gratuito
GROQ_MODEL = "llama-3.3-70b-versatile"

# Pausa entre llamadas a la API para no saturar el rate limit (requests/min)
API_CALL_DELAY_S = 2.0

# Máximo de tokens por respuesta
MAX_TOKENS = 300

# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
Eres un asistente experto en Python que escribe docstrings profesionales en español.

Reglas estrictas:
- Escribe SOLO el docstring, sin código adicional, sin bloques ```python, sin explicaciones.
- El docstring debe empezar y terminar con triple comillas dobles (\"\"\").
- Primera línea: resumen conciso en una sola frase.
- Si tiene parámetros relevantes, añade sección Args:.
- Si tiene retorno relevante, añade sección Returns:.
- Si puede lanzar excepciones relevantes, añade sección Raises:.
- Usa estilo Google Docstrings.
- Máximo 8 líneas. Sé preciso y útil, no genérico.
- No repitas el nombre de la función en el resumen.
"""

def build_prompt(kind: str, name: str, signature: str, source_code: str, class_name: str = "") -> str:
    """Construye el prompt para un elemento concreto."""
    context = f"de la clase `{class_name}`" if class_name else "de módulo"
    return (
        f"Escribe un docstring profesional en español para el siguiente {kind} {context}:\n\n"
        f"Nombre: `{name}`\n"
        f"Firma: `{signature}`\n\n"
        f"Código:\n```python\n{source_code}\n```\n\n"
        f"Responde ÚNICAMENTE con el docstring, empezando con \\\"\\\"\\\". "
        f"Sin código adicional, sin bloques de código Markdown."
    )

# ── AST helpers ───────────────────────────────────────────────────────────────

def get_function_signature(node: ast.FunctionDef) -> str:
    """Construye la firma legible de una función."""
    try:
        args = []
        fn_args = node.args

        n_args = len(fn_args.args)
        n_defaults = len(fn_args.defaults)
        defaults_map = {}
        for i, default in enumerate(fn_args.defaults):
            arg_index = n_args - n_defaults + i
            try:
                defaults_map[fn_args.args[arg_index].arg] = ast.unparse(default)
            except Exception:
                pass

        for arg in fn_args.args:
            part = arg.arg
            if arg.annotation:
                part += f": {ast.unparse(arg.annotation)}"
            if arg.arg in defaults_map:
                part += f" = {defaults_map[arg.arg]}"
            args.append(part)

        if fn_args.vararg:
            args.append(f"*{fn_args.vararg.arg}")
        if fn_args.kwarg:
            args.append(f"**{fn_args.kwarg.arg}")

        ret = ""
        if node.returns:
            ret = f" -> {ast.unparse(node.returns)}"

        return f"{node.name}({', '.join(args)}){ret}"
    except Exception:
        return f"{node.name}(...)"


def get_node_source(source_lines: list[str], node: ast.AST) -> str:
    """Extrae el código fuente de un nodo AST (máx 30 líneas para no saturar el prompt)."""
    start = node.lineno - 1
    end = getattr(node, "end_lineno", start + 20)
    snippet = source_lines[start:min(end, start + 30)]
    return textwrap.dedent("".join(snippet)).strip()


def has_real_docstring(node: ast.AST) -> bool:
    """Comprueba si el nodo tiene ya un docstring real (no flotante)."""
    return bool(ast.get_docstring(node))


def insert_or_replace_docstring(
    source_lines: list[str],
    node: ast.FunctionDef | ast.ClassDef,
    new_docstring: str,
) -> list[str]:
    """
    Inserta o reemplaza el docstring de un nodo en source_lines.
    Devuelve la lista de líneas modificada.
    """
    # Indentación del cuerpo del nodo
    body_start = node.body[0]
    indent = " " * (body_start.col_offset)

    # Formatear el docstring con indentación correcta
    doc_lines = new_docstring.strip().splitlines()
    if len(doc_lines) == 1:
        formatted = f'{indent}{doc_lines[0]}\n'
    else:
        formatted_parts = [f'{indent}{doc_lines[0]}\n']
        for line in doc_lines[1:-1]:
            formatted_parts.append(f'{indent}{line}\n' if line.strip() else '\n')
        formatted_parts.append(f'{indent}{doc_lines[-1]}\n')
        formatted = "".join(formatted_parts)

    lines = list(source_lines)

    # Si ya tiene docstring, reemplazarlo
    if has_real_docstring(node):
        existing = node.body[0]
        # existing es un ast.Expr con un ast.Constant
        start_line = existing.lineno - 1      # índice 0-based
        end_line = existing.end_lineno        # exclusivo (1-based end → 0-based exclusivo)
        lines[start_line:end_line] = [formatted]
    else:
        # Insertar después de la línea def/class
        # El body[0] es el primer statement — insertar antes de él
        insert_at = body_start.lineno - 1
        lines.insert(insert_at, formatted)

    return lines


# ── Generación via Groq ────────────────────────────────────────────────────────

def generate_docstring(client: Groq, prompt: str) -> str | None:
    """Llama a la API de Groq y devuelve el docstring generado o None si falla."""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=MAX_TOKENS,
            temperature=0.2,
        )
        text = response.choices[0].message.content.strip()

        # Limpiar bloques Markdown si el modelo los añade igualmente
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        # Asegurar que empieza y termina con triple comillas
        if not text.startswith('"""'):
            text = '"""' + text
        if not text.endswith('"""'):
            text = text + '"""'

        return text
    except Exception as e:
        print(f"     ⚠️  Error API: {e}")
        return None


# ── Procesado de un archivo ────────────────────────────────────────────────────

def process_file(
    py_file: Path,
    client: Groq,
    dry_run: bool,
    regenerate_all: bool,
) -> tuple[int, int]:
    """
    Procesa un archivo .py y genera/regenera docstrings.
    Devuelve (generados, errores).
    """
    source = py_file.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  ⚠️  SyntaxError en {py_file.name}: {e}")
        return 0, 0

    source_lines = source.splitlines(keepends=True)
    generated = 0
    errors = 0

    # Recopilar todos los nodos a procesar con su contexto
    tasks: list[tuple[ast.AST, str, str, str]] = []  # (node, kind, name, class_name)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if regenerate_all or not has_real_docstring(node):
                tasks.append((node, "función", node.name, ""))
        elif isinstance(node, ast.ClassDef):
            if regenerate_all or not has_real_docstring(node):
                tasks.append((node, "clase", node.name, ""))
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if regenerate_all or not has_real_docstring(item):
                        tasks.append((item, "método", item.name, node.name))

    if not tasks:
        print(f"  ✓  {py_file.name} — sin cambios necesarios")
        return 0, 0

    print(f"  📝 {py_file.name} — {len(tasks)} elemento(s) a documentar")

    # Procesar en orden inverso para que los offsets de línea no se desplacen
    # al modificar el archivo (los nodos de más abajo primero)
    tasks_sorted = sorted(tasks, key=lambda t: t[0].lineno, reverse=True)

    current_lines = list(source_lines)

    for node, kind, name, class_name in tasks_sorted:
        display = f"{class_name}.{name}" if class_name else name
        print(f"     → {kind} `{display}`", end=" ", flush=True)

        sig = get_function_signature(node) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else name
        snippet = get_node_source(source_lines, node)
        prompt = build_prompt(kind, name, sig, snippet, class_name)

        if dry_run:
            print("(dry-run, omitido)")
            continue

        docstring = generate_docstring(client, prompt)
        time.sleep(API_CALL_DELAY_S)

        if docstring:
            current_lines = insert_or_replace_docstring(current_lines, node, docstring)
            print("✓")
            generated += 1
        else:
            print("✗ (error API)")
            errors += 1

    if not dry_run and generated > 0:
        py_file.write_text("".join(current_lines), encoding="utf-8")
        print(f"     💾 Guardado ({generated} docstrings escritos)")

    return generated, errors


# ── Recolección de archivos ────────────────────────────────────────────────────

def collect_py_files(project_root: Path, layer_filter: str = None) -> list[Path]:
    """
    Recolecta todos los .py de las capas configuradas.
    Si layer_filter está definido, solo procesa esa capa (ej: 'core', 'ui/windows').
    """
    layers = [layer_filter + "/"] if layer_filter else LAYERS
    files = []
    seen = set()
    for layer in layers:
        target = project_root / layer
        if not target.exists():
            print(f"⚠️  Capa no encontrada: {layer}")
            continue
        for py_file in sorted(target.rglob("*.py")):
            if "__pycache__" in py_file.parts:
                continue
            if py_file.resolve() not in seen:
                seen.add(py_file.resolve())
                files.append(py_file)
    return files


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Genera/regenera docstrings en español via Groq API."
    )
    parser.add_argument("project_root", help="Ruta raíz del proyecto")
    parser.add_argument("--api-key", help="Groq API key (o usa GROQ_API_KEY env)")
    parser.add_argument("--file", help="Procesar solo este archivo .py (ruta relativa al proyecto)")
    parser.add_argument("--layer", help="Procesar solo una capa: core, ui, ui/windows, config, utils")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin escribir cambios")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ Falta la API key. Usa --api-key o exporta GROQ_API_KEY=gsk_...")
        sys.exit(1)

    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        print(f"❌ No existe: {project_root}")
        sys.exit(1)

    client = Groq(api_key=api_key)

    if args.file:
        py_files = [project_root / args.file]
    elif args.layer:
        py_files = collect_py_files(project_root, layer_filter=args.layer)
    else:
        py_files = collect_py_files(project_root)

    if not py_files:
        print("❌ No se encontraron archivos .py")
        sys.exit(1)

    mode = "DRY-RUN" if args.dry_run else "REGENERAR TODOS"
    scope = args.layer or args.file or "proyecto completo"
    print(f"\n🚀 Dashboard RPi — Generador de docstrings via Groq")
    print(f"   Modo    : {mode}")
    print(f"   Alcance : {scope}")
    print(f"   Modelo  : {GROQ_MODEL}")
    print(f"   Archivos: {len(py_files)}")
    print(f"   Delay   : {API_CALL_DELAY_S}s entre llamadas\n")

    total_generated = 0
    total_errors = 0

    for py_file in py_files:
        rel = py_file.relative_to(project_root)
        print(f"\n📄 {rel}")
        gen, err = process_file(
            py_file,
            client,
            dry_run=args.dry_run,
            regenerate_all=True,
        )
        total_generated += gen
        total_errors += err

    print(f"\n{'─' * 50}")
    print(f"✅ Completado: {total_generated} docstrings generados")
    if total_errors:
        print(f"⚠️  Errores API: {total_errors} (revisar manualmente)")
    print(f"{'─' * 50}\n")


if __name__ == "__main__":
    main()
