"""
PitchGen - A microservice that generates deterministic pitch statements.

This package provides both a CLI interface and an HTTP API for generating
product pitches based on input parameters.
"""

__version__ = "1.0.0"
__author__ = "PitchGen Team"

from pitchgen.core import generate_pitch, PitchRequest, PitchResponse

__all__ = ["generate_pitch", "PitchRequest", "PitchResponse"]
