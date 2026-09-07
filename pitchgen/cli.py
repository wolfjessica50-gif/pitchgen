#!/usr/bin/env python3
"""
PitchGen CLI - Command-line interface for pitch generation.

Usage:
    pitchgen --product-name "Widget" --one-liner "revolutionary tool" \\
             --target-audience "developers" --primary-value "speed" \\
             --tone friendly --length short

    echo '{"product_name": "Widget", ...}' | pitchgen --json

Examples:
    # Basic usage with arguments
    pitchgen --product-name "Widget" --one-liner "a game changer" \\
             --target-audience "startups" --primary-value "growth"
    
    # With specific tone and length
    pitchgen --product-name "Widget" --one-liner "a game changer" \\
             --target-audience "startups" --primary-value "growth" \\
             --tone formal --length medium
    
    # Read from JSON file
    pitchgen --input input.json
    
    # Read from stdin
    cat input.json | pitchgen --json
"""

import argparse
import json
import sys
from typing import Optional, TextIO

from pitchgen.core import generate_pitch, validate_request, PitchResponse


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pitchgen",
        description="Generate product pitch statements from command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --product-name Widget --one-liner "a game changer" \\
           --target-audience startups --primary-value growth
  
  %(prog)s --product-name Widget --one-liner "a game changer" \\
           --target-audience startups --primary-value growth \\
           --tone formal --length medium
  
  %(prog)s --input input.json
  cat input.json | %(prog)s --json
        """,
    )
    
    # Input mode group (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "-i", "--input",
        type=argparse.FileType("r"),
        default=None,
        help="Input JSON file (default: stdin with --json flag)",
    )
    input_group.add_argument(
        "-j", "--json",
        action="store_true",
        help="Read JSON input from stdin",
    )
    
    # Required product fields
    parser.add_argument(
        "-p", "--product-name",
        type=str,
        default=None,
        help="Name of the product (required without --json/--input)",
    )
    parser.add_argument(
        "-o", "--one-liner",
        type=str,
        default=None,
        help="One-line description of the product (required without --json/--input)",
    )
    parser.add_argument(
        "-a", "--target-audience",
        type=str,
        default=None,
        help="Intended audience for the product (required without --json/--input)",
    )
    parser.add_argument(
        "-v", "--primary-value",
        type=str,
        default=None,
        help="Primary value proposition (required without --json/--input)",
    )
    
    # Optional parameters
    parser.add_argument(
        "-t", "--tone",
        type=str,
        choices=["formal", "casual", "humorous", "inspirational", "friendly"],
        default="friendly",
        help="Tone of the pitch (default: friendly)",
    )
    parser.add_argument(
        "-l", "--length",
        type=str,
        choices=["short", "medium", "long"],
        default="medium",
        help="Length of the pitch (default: medium)",
    )
    
    # Output options
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information",
    )
    
    return parser


def read_json_input(source: Optional[TextIO] = None) -> dict:
    """Read and parse JSON from a file or stdin."""
    if source is None:
        source = sys.stdin
    
    try:
        content = source.read()
        if not content.strip():
            raise ValueError("Empty input")
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Error reading input: {e}")


def dict_to_pitch_request(data: dict) -> tuple:
    """
    Convert a dictionary to validated pitch request fields.
    
    Returns:
        Tuple of (product_name, one_liner, target_audience, primary_value, tone, length)
    """
    return (
        data.get("product_name") or data.get("product-name"),
        data.get("one_liner") or data.get("one-liner"),
        data.get("target_audience") or data.get("target-audience"),
        data.get("primary_value") or data.get("primary-value"),
        data.get("tone"),
        data.get("length"),
    )


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the PitchGen CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    # Handle version flag
    if parsed.version:
        from pitchgen import __version__
        print(f"pitchgen {__version__}")
        return 0
    
    try:
        # Determine input source and mode
        if parsed.json:
            input_data = read_json_input()
            product_name, one_liner, target_audience, primary_value, tone, length = dict_to_pitch_request(input_data)
        elif parsed.input:
            input_data = read_json_input(parsed.input)
            product_name, one_liner, target_audience, primary_value, tone, length = dict_to_pitch_request(input_data)
        else:
            # Use command line arguments
            product_name = parsed.product_name
            one_liner = parsed.one_liner
            target_audience = parsed.target_audience
            primary_value = parsed.primary_value
            tone = parsed.tone
            length = parsed.length
        
        # Validate and create request
        request = validate_request(
            product_name=product_name,
            one_liner=one_liner,
            target_audience=target_audience,
            primary_value=primary_value,
            tone=tone,
            length=length,
        )
        
        # Generate pitch
        response = generate_pitch(request)
        
        # Output result
        if parsed.format == "json":
            print(json.dumps({"pitch": response.pitch}, indent=2))
        else:
            print(response.pitch)
        
        return 0
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        parser.print_help(file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
