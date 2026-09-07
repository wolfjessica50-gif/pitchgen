"""
Unit tests for PitchGen CLI.

Run with:
    python -m pytest pitchgen/tests/test_cli.py -v
    python -m unittest pitchgen/tests/test_cli.py -v
"""

import unittest
import sys
import json
from io import StringIO
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, "/root/automaton/projects/01M1X4D6M4HJA3JX8ME2N432A2")

from pitchgen.cli import main, create_parser, read_json_input, dict_to_pitch_request


class TestPitchGenCLI(unittest.TestCase):
    """Test cases for PitchGen CLI functionality."""

    def test_parser_help(self):
        """Test that --help displays usage without errors."""
        parser = create_parser()
        # Should not raise
        parser.parse_args(["--help"])

    def test_parser_minimal_args(self):
        """Test parser accepts minimal required arguments."""
        parser = create_parser()
        args = parser.parse_args([
            "--product-name", "TestProduct",
            "--one-liner", "A test product",
            "--target-audience", "testers",
            "--primary-value", "testing",
        ])
        self.assertEqual(args.product_name, "TestProduct")
        self.assertEqual(args.one_liner, "A test product")
        self.assertEqual(args.target_audience, "testers")
        self.assertEqual(args.primary_value, "testing")
        self.assertEqual(args.tone, "friendly")  # default
        self.assertEqual(args.length, "medium")  # default

    def test_parser_all_args(self):
        """Test parser accepts all arguments."""
        parser = create_parser()
        args = parser.parse_args([
            "--product-name", "TestProduct",
            "--one-liner", "A test product",
            "--target-audience", "testers",
            "--primary-value", "testing",
            "--tone", "formal",
            "--length", "long",
        ])
        self.assertEqual(args.tone, "formal")
        self.assertEqual(args.length, "long")

    def test_parser_short_flags(self):
        """Test parser accepts short flag variants."""
        parser = create_parser()
        args = parser.parse_args([
            "-p", "TestProduct",
            "-o", "A test product",
            "-a", "testers",
            "-v", "testing",
        ])
        self.assertEqual(args.product_name, "TestProduct")

    def test_dict_to_pitch_request_underscore_keys(self):
        """Test conversion from dict with underscore keys."""
        data = {
            "product_name": "Widget",
            "one_liner": "great product",
            "target_audience": "everyone",
            "primary_value": "joy",
            "tone": "casual",
            "length": "short",
        }
        result = dict_to_pitch_request(data)
        self.assertEqual(result, ("Widget", "great product", "everyone", "joy", "casual", "short"))

    def test_dict_to_pitch_request_dash_keys(self):
        """Test conversion from dict with dash keys (CLI-style)."""
        data = {
            "product-name": "Widget",
            "one-liner": "great product",
            "target-audience": "everyone",
            "primary-value": "joy",
        }
        result = dict_to_pitch_request(data)
        self.assertEqual(result, ("Widget", "great product", "everyone", "joy", None, None))

    def test_read_json_input_valid(self):
        """Test reading valid JSON from string."""
        json_str = '{"product_name": "Test", "one_liner": "test"}'
        result = read_json_input(StringIO(json_str))
        self.assertEqual(result["product_name"], "Test")

    def test_read_json_input_invalid(self):
        """Test reading invalid JSON raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            read_json_input(StringIO("not valid json"))
        self.assertIn("Invalid JSON", str(ctx.exception))

    def test_read_json_input_empty(self):
        """Test reading empty JSON raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            read_json_input(StringIO(""))
        self.assertIn("Empty input", str(ctx.exception))

    def test_main_minimal_args(self):
        """Test main with minimal command line arguments."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = main([
                "--product-name", "TestProduct",
                "--one-liner", "A test product",
                "--target-audience", "testers",
                "--primary-value", "testing",
            ])
        self.assertEqual(exit_code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("TestProduct", output)

    def test_main_all_tones(self):
        """Test main generates different output for different tones."""
        for tone in ["formal", "casual", "humorous", "inspirational", "friendly"]:
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                exit_code = main([
                    "--product-name", "TestProduct",
                    "--one-liner", "A test product",
                    "--target-audience", "testers",
                    "--primary-value", "testing",
                    "--tone", tone,
                    "--format", "text",
                ])
            self.assertEqual(exit_code, 0)

    def test_main_all_lengths(self):
        """Test main generates different output for different lengths."""
        for length in ["short", "medium", "long"]:
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                exit_code = main([
                    "--product-name", "TestProduct",
                    "--one-liner", "A test product",
                    "--target-audience", "testers",
                    "--primary-value", "testing",
                    "--length", length,
                ])
            self.assertEqual(exit_code, 0)

    def test_main_json_output(self):
        """Test main outputs valid JSON when --format json."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = main([
                "--product-name", "TestProduct",
                "--one-liner", "A test product",
                "--target-audience", "testers",
                "--primary-value", "testing",
                "--format", "json",
            ])
        self.assertEqual(exit_code, 0)
        output = mock_stdout.getvalue()
        # Should be valid JSON
        parsed = json.loads(output)
        self.assertIn("pitch", parsed)

    def test_main_json_input(self):
        """Test main reads from stdin with --json flag."""
        json_input = json.dumps({
            "product_name": "TestProduct",
            "one_liner": "A test product",
            "target_audience": "testers",
            "primary_value": "testing",
        })
        with patch("sys.stdin", new_callable=lambda: StringIO(json_input)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                exit_code = main(["--json"])
        self.assertEqual(exit_code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("TestProduct", output)

    def test_main_missing_required_args(self):
        """Test main returns error when required arguments are missing."""
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            exit_code = main([])
        self.assertEqual(exit_code, 1)

    def test_main_invalid_tone(self):
        """Test main rejects invalid tone."""
        with patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit) as ctx:
                main([
                    "--product-name", "TestProduct",
                    "--one-liner", "A test product",
                    "--target-audience", "testers",
                    "--primary-value", "testing",
                    "--tone", "invalid_tone",
                ])
        # argparse exits with code 2 for invalid arguments
        self.assertEqual(ctx.exception.code, 2)

    def test_main_version_flag(self):
        """Test --version flag works."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = main(["--version"])
        self.assertEqual(exit_code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("pitchgen", output.lower())

    def test_main_invalid_json_input(self):
        """Test main handles invalid JSON input gracefully."""
        with patch("sys.stdin", new_callable=lambda: StringIO("not json")):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                exit_code = main(["--json"])
        self.assertEqual(exit_code, 1)


class TestPitchGenCore(unittest.TestCase):
    """Test cases for PitchGen core functionality."""

    def test_generate_pitch_basic(self):
        """Test basic pitch generation."""
        from pitchgen.core import generate_pitch, PitchRequest
        
        request = PitchRequest(
            product_name="TestProduct",
            one_liner="a revolutionary tool",
            target_audience="developers",
            primary_value="productivity",
            tone="friendly",
            length="short",
        )
        response = generate_pitch(request)
        self.assertIn("TestProduct", response.pitch)
        self.assertIn("developers", response.pitch)

    def test_generate_pitch_all_tones(self):
        """Test pitch generation with all tone options."""
        from pitchgen.core import generate_pitch, PitchRequest
        
        for tone in ["formal", "casual", "humorous", "inspirational", "friendly"]:
            request = PitchRequest(
                product_name="X",
                one_liner="Y",
                target_audience="Z",
                primary_value="W",
                tone=tone,
                length="medium",
            )
            response = generate_pitch(request)
            self.assertTrue(len(response.pitch) > 0)

    def test_generate_pitch_all_lengths(self):
        """Test pitch generation with all length options."""
        from pitchgen.core import generate_pitch, PitchRequest
        
        for length in ["short", "medium", "long"]:
            request = PitchRequest(
                product_name="X",
                one_liner="Y",
                target_audience="Z",
                primary_value="W",
                tone="friendly",
                length=length,
            )
            response = generate_pitch(request)
            self.assertTrue(len(response.pitch) > 0)

    def test_validate_request_valid(self):
        """Test validation accepts valid input."""
        from pitchgen.core import validate_request
        
        result = validate_request(
            product_name="Test",
            one_liner="A test",
            target_audience="Testers",
            primary_value="Testing",
        )
        self.assertEqual(result.product_name, "Test")
        self.assertEqual(result.tone, "friendly")  # default

    def test_validate_request_missing_field(self):
        """Test validation rejects missing required fields."""
        from pitchgen.core import validate_request
        
        with self.assertRaises(ValueError) as ctx:
            validate_request(
                product_name="Test",
                # missing one_liner
                target_audience="Testers",
                primary_value="Testing",
            )
        self.assertIn("one_liner is required", str(ctx.exception))

    def test_validate_request_invalid_tone(self):
        """Test validation rejects invalid tone."""
        from pitchgen.core import validate_request
        
        with self.assertRaises(ValueError) as ctx:
            validate_request(
                product_name="Test",
                one_liner="A test",
                target_audience="Testers",
                primary_value="Testing",
                tone="invalid",
            )
        self.assertIn("tone must be one of", str(ctx.exception))

    def test_validate_request_invalid_length(self):
        """Test validation rejects invalid length."""
        from pitchgen.core import validate_request
        
        with self.assertRaises(ValueError) as ctx:
            validate_request(
                product_name="Test",
                one_liner="A test",
                target_audience="Testers",
                primary_value="Testing",
                length="invalid",
            )
        self.assertIn("length must be one of", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
