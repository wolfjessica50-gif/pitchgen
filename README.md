# PitchGen: Marketing Pitch Generator

## Overview

PitchGen is a comprehensive marketing pitch generation tool that creates compelling marketing pitches for products and services. It combines template-based pitch generation with structured output in both JSON and Markdown formats.

## Features

- **Template-based pitch generation**: Creates marketing pitches using proven templates
- **CLI interface**: Command-line tool for easy integration
- **Dual output formats**: JSON data structure and human-readable Markdown preview
- **Flexible input**: Accepts JSON input from files or stdin, with individual field support
- **Standardized schemas**: Pydantic-validated input/output structures

## Installation

### Prerequisites

- Python 3.7+
- pip

### Installation Steps

```bash
# Clone the repository
cgit clone <repository-url>
cd pitchgen-demo

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic

# For the CLI specifically, only standard library is required for basic operation
```

## CLI Usage

### Basic Usage

```bash
# Generate a pitch from a JSON file
pitchgen input.json

# Generate a pitch from stdin
pitchgen --stdin
```

### Help and Options

```bash
# Show main help
pitchgen --help

# Show generate command help
pitchgen generate --help
```

### Output Formats

```bash
# Generate JSON output only
pitchgen input.json --format json

# Generate Markdown output only
pitchgen input.json --format markdown

# Generate both formats
pitchgen input.json --format both
```

## Input Schema

PitchGen accepts a JSON object with the following fields:

- `product_name` (string, required): The name of the product or service
- `target_audience` (string, required): The target customer segment
- `key_features` (array, optional): List of product features
- `value_proposition` (string, optional): Core value proposition

### Example Input JSON

```json
{
  "product_name": "SuperWidget",
  "target_audience": "software developers",
  "key_features": [
    "Instant integration",
    "Zero configuration",
    "Unlimited scaling"
  ],
  "value_proposition": "Transform your workflow with our revolutionary solution"
}
```

### Individual Field Arguments

The CLI also supports generating pitches using individual command-line arguments:

```bash
pitchgen generate \
  --product-name "SuperWidget" \
  --target-audience "developers" \
  --key-features "integration" "configuration" "scaling" \
  --value-proposition "Transform your workflow"
```

## Output Formats

### JSON Output

```json
{
  "pitch": {
    "generated_pitch": "Your compelling marketing pitch here...",
    "word_count": 150,
    "key_points": ["point1", "point2", "point3"],
    "target_audience_focused": true,
    "generated_at": "2026-09-07T05:16:56Z"
  },
  "metadata": {
    "model": "template-based",
    "version": "1.0.0",
    "processing_time_ms": 125
  }
}
```

### Markdown Output

```markdown
# Marketing Pitch for SuperWidget

## Overview
Transform your workflow with our revolutionary solution.

## For Developers
- **Instant integration** - Get started in minutes
- **Zero configuration** - Deploy instantly
- **Unlimited scaling** - Grow without limits

## Key Benefits
1. Save time and resources
2. Increase productivity
3. Enhance user experience

---
*Generated using PitchGen v1.0.0*
```

## HTTP API

PitchGen also includes a FastAPI HTTP service for web integration:

### Endpoints

- `GET /health`: Service health check
- `POST /generate`: Generate a pitch from JSON input

### API Usage

```bash
# Generate a pitch via HTTP
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"product_name": "SuperWidget", "target_audience": "developers"}'
```

## Testing

### Running Tests

```bash
# Run smoke tests
cd pitchgen-demo
./smoke_test.sh
```

### Test Scripts

The project includes several test scripts:

- `smoke_test.sh`: End-to-end functional test
- `pitchgen_test.sh`: Integration test
- `pitchgen_demo_test.sh`: Demo-specific tests

## Project Structure

```
pitchgen/
├── cli.py              # CLI entry point
├── app.py              # FastAPI application
├── pitchgen_demo.py    # Main pitch generation logic
├── server.py           # HTTP server implementation
├── smoke_test.sh       # Testing script
└── README.md          # This file
```

## Contribution Guidelines

### Code Standards

- **Python version**: Use Python 3.7+
- **Code style**: PEP 8 compliant
- **Type hints**: Include type annotations
- **Testing**: Write tests for new functionality
- **Documentation**: Update README with new features

### Adding New Features

1. **Feature implementation**: Implement new pitch generation features in `pitchgen_demo.py`
2. **CLI support**: Add CLI arguments in `cli.py`
3. **API support**: Add endpoints in `app.py` (FastAPI)
4. **Testing**: Write tests in the `test/` directory
5. **Documentation**: Update this README with usage examples

### Running Development Server

```bash
cd pitchgen-demo
uvicorn app:app --reload
```

## Development Workflow

1. **Code changes**: Modify `cli.py`, `app.py`, or `pitchgen_demo.py` as needed
2. **Testing**: Run `smoke_test.sh` to verify functionality
3. **Documentation**: Update README with new usage examples
4. **API testing**: Test with curl commands above
5. **Code review**: Ensure all changes follow project conventions

## Next Steps

1. **Try it out**: Generate your first pitch with a sample input
2. **Explore API**: Test the HTTP endpoints with your own requests
3. **Contribute**: Add new pitch templates or improve generation logic
4. **Create integrations**: Build web applications or services using PitchGen

## Support and Issues

- **Documentation**: This README and the code comments
- **Issue tracking**: File issues in the repository
- **Community**: Join discussions in the project

## License

This project is licensed under the terms of the MIT License.

---

## Quick Start Example

```bash
# 1. Create a sample input file
sample_input.json << EOF
{
  "product_name": "AI Content Generator",
  "target_audience": "content creators",
  "key_features": [
    "Generate articles",
    "Create social media posts",
    "Write code documentation"
  ],
  "value_proposition": "Supercharge your content creation workflow"
}
EOF

# 2. Generate a pitch
pitchgen sample_input.json --format both

# 3. View the results
# Check output.json for structured data
# Check output.md for readable marketing pitch
```

This README provides a comprehensive guide to using PitchGen for marketing pitch generation. For more information, refer to individual source files or contact the development team.