import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.input_manager import InputManager
from src.source_detector import SourceDetector
from src.metadata_analyzer import MetadataAnalyzer
from src.metadata_validator import MetadataValidator
from src.citation_generator import CitationGenerator
from src.bibliography_builder import BibliographyBuilder
from src.output_validator import OutputValidator
from src.models import Reference


def process_single(raw_input: str, style: str, index: int = 1) -> Reference:
    input_mgr = InputManager()
    detector = SourceDetector()
    analyzer = MetadataAnalyzer()
    validator = MetadataValidator()
    generator = CitationGenerator()

    input_type = input_mgr.detect_type(raw_input)
    validation_warnings = input_mgr.validate(raw_input, input_type)

    source_type = detector.detect(raw_input, input_type)
    metadata = analyzer.analyze(raw_input, input_type, source_type)
    validator.validate(metadata)

    citation = generator.generate(metadata, style, index)

    ref = Reference(
        raw_input=raw_input,
        input_type=input_type,
        source_type=metadata.source_type,
        metadata=metadata,
        citation=citation,
        index=index,
        warnings=metadata.warnings + validation_warnings,
    )
    return ref


def process_multiple(inputs: list[str], style: str) -> tuple[list[Reference], str, list[str]]:
    expanded = []
    for inp in inputs:
        stripped = inp.strip()
        if stripped.startswith("["):
            try:
                items = json.loads(stripped)
                for item in items:
                    if isinstance(item, str):
                        expanded.append(item)
                    elif isinstance(item, dict):
                        expanded.append(json.dumps(item))
                continue
            except json.JSONDecodeError:
                pass
        expanded.append(inp)

    refs = []
    for i, inp in enumerate(expanded, 1):
        refs.append(process_single(inp, style, i))

    builder = BibliographyBuilder()
    validator = OutputValidator()

    refs = builder.remove_duplicates(refs)
    refs = builder.assign_indices(refs, style)
    bibliography = builder.build(refs, style)
    issues = validator.validate(refs, style)

    return refs, bibliography, issues


def format_text_output(refs: list[Reference], style: str, bibliography: str, issues: list[str]) -> str:
    lines = []
    lines.append(f"=== Citations ({style.upper()}) ===")
    for ref in refs:
        lines.append(ref.citation or "")
    lines.append("")

    lines.append("=== Bibliography ===")
    lines.append(bibliography)
    lines.append("")

    all_warnings = []
    for ref in refs:
        all_warnings.extend(ref.warnings)
    all_warnings.extend(issues)

    if all_warnings:
        lines.append("=== Warnings ===")
        for w in all_warnings:
            lines.append(f"  ! {w}")
        lines.append("")

    return "\n".join(lines)


def format_json_output(refs: list[Reference], style: str, bibliography: str, issues: list[str]) -> str:
    all_warnings = []
    for ref in refs:
        all_warnings.extend(ref.warnings)
    all_warnings.extend(issues)

    result = {
        "status": "success",
        "citation_style": style,
        "citations": [ref.citation for ref in refs],
        "bibliography": bibliography,
        "warnings": all_warnings,
        "references": [
            {
                "title": ref.metadata.title if ref.metadata else None,
                "authors": ref.metadata.authors if ref.metadata else [],
                "year": ref.metadata.year if ref.metadata else None,
                "doi": ref.metadata.doi if ref.metadata else None,
                "source_type": ref.source_type,
            }
            for ref in refs
        ],
    }
    return json.dumps(result, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="SCRA - Smart Citation & Reference Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python main.py "Attention Is All You Need"
  python main.py "10.1145/3368089.3409741"
  python main.py "https://github.com/example/repo" --style ieee
  python main.py --file refs.json --style apa --output json
  python main.py --interactive
        """,
    )
    parser.add_argument("input", nargs="?", help="Referensi (URL/DOI/Judul/JSON)")
    parser.add_argument("--style", choices=["ieee", "apa"], default="ieee", help="Style sitasi (default: ieee)")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Format output (default: text)")
    parser.add_argument("--file", help="File JSON berisi daftar referensi")
    parser.add_argument("--interactive", action="store_true", help="Mode interaktif")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode(args.style, args.output)
        return

    inputs = []
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                inputs = [json.dumps(item) if isinstance(item, dict) else str(item) for item in data]
            else:
                inputs = [json.dumps(data)]
        except Exception as e:
            print(f"Error membaca file: {e}")
            sys.exit(1)
    elif args.input:
        inputs = [args.input]
    else:
        parser.print_help()
        return

    try:
        refs, bibliography, issues = process_multiple(inputs, args.style)
        if args.output == "json":
            print(format_json_output(refs, args.style, bibliography, issues))
        else:
            print(format_text_output(refs, args.style, bibliography, issues))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def interactive_mode(style: str, output_format: str):
    print("SCRA - Smart Citation & Reference Agent (interactive)")
    print("Ketik referensi, atau 'exit' untuk keluar.\n")
    while True:
        try:
            inp = input(">>> ").strip()
            if inp.lower() in ("exit", "quit", "q"):
                break
            if not inp:
                continue
            refs, bibliography, issues = process_multiple([inp], style)
            print(format_text_output(refs, style, bibliography, issues))
        except KeyboardInterrupt:
            print()
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
