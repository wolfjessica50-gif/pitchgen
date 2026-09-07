"""
Core pitch generation logic for PitchGen.

This module contains the business logic for generating deterministic
product pitches based on input parameters.
"""

from dataclasses import dataclass
from typing import List, Literal, Optional


@dataclass
class PitchRequest:
    """Input parameters for pitch generation."""
    product_name: str
    one_liner: str
    target_audience: str
    primary_value: str
    tone: Literal["formal", "casual", "humorous", "inspirational", "friendly"]
    length: Literal["short", "medium", "long"]


@dataclass
class PitchResponse:
    """Generated pitch output."""
    pitch: str


def generate_pitch(request: PitchRequest) -> PitchResponse:
    """
    Generate a deterministic product pitch based on input parameters.
    
    Args:
        request: PitchRequest containing product details and preferences.
        
    Returns:
        PitchResponse with the generated pitch text.
    """
    # Build base pitch template
    template_map = {
        "short": {
            "formal": "{product}: {one_liner} for {audience}. Delivers {value}.",
            "casual": "{product} - {one_liner}! Great for {audience}. {value}!",
            "humorous": "Behold {product}! {one_liner} (no, seriously). For {audience}.",
            "inspirational": "{product}: Transform {one_liner} for {audience}. {value}!",
            "friendly": "Check out {product}! {one_liner} for {audience}. {value}!",
        },
        "medium": {
            "formal": "{product} is {one_liner}. Designed for {audience}, it delivers {value}. A professional solution for modern needs.",
            "casual": "{product} is here - {one_liner}! Built specifically for {audience}. It brings you {value}. Try it today!",
            "humorous": "{product} enters the scene: {one_liner}. Yes, {audience}, you read that right. {value}.",
            "inspirational": "{product} represents {one_liner}. For {audience}, it offers {value}. This changes everything.",
            "friendly": "Meet {product}! {one_liner} - perfect for {audience}. You'll love {value}!",
        },
        "long": {
            "formal": "{product} is proud to introduce {one_liner}. Created specifically for {audience}, this solution delivers {value}. With a focus on quality and reliability, {product} provides enterprise-grade functionality that meets the demands of modern businesses. Whether you're just starting out or scaling operations, {product} adapts to your needs.",
            "casual": "Hey {audience}! Get ready for {product} - {one_liner}! We've built something special that delivers {value}. It's designed to make your life easier, whether you're working solo or with a team. Check it out and see the difference!",
            "humorous": "Ladies and gentlemen, boys and girls, {product} has arrived: {one_liner}! For {audience} who thought they've seen it all - think again! We promise {value}. Side effects may include productivity, happiness, and wondering how you ever lived without us.",
            "inspirational": "{product} is more than software - it's {one_liner}. Built for visionary {audience}, it delivers {value}. Every great journey begins with a single step, and {product} is that step. Join us in redefining what's possible.",
            "friendly": "We're excited to introduce {product}! {one_liner} - made with love for {audience}. It brings you {value}, wrapped in an experience you'll actually enjoy. We believe great tools should feel great to use. Welcome to {product}!",
        },
    }
    
    tone_templates = template_map.get(request.length, template_map["medium"])
    template = tone_templates.get(request.tone, tone_templates["friendly"])
    
    pitch = template.format(
        product=request.product_name,
        one_liner=request.one_liner,
        audience=request.target_audience,
        value=request.primary_value,
    )
    
    return PitchResponse(pitch=pitch)


def validate_request(
    product_name: Optional[str] = None,
    one_liner: Optional[str] = None,
    target_audience: Optional[str] = None,
    primary_value: Optional[str] = None,
    tone: Optional[str] = None,
    length: Optional[str] = None,
) -> PitchRequest:
    """
    Validate and create a PitchRequest from raw inputs.
    
    Args:
        product_name: Name of the product
        one_liner: Brief one-line description
        target_audience: Intended audience
        primary_value: Main value proposition
        tone: Desired tone (formal, casual, humorous, inspirational, friendly)
        length: Desired length (short, medium, long)
        
    Returns:
        Validated PitchRequest
        
    Raises:
        ValueError: If any required field is missing or invalid
    """
    valid_tones = {"formal", "casual", "humorous", "inspirational", "friendly"}
    valid_lengths = {"short", "medium", "long"}
    
    errors = []
    
    if not product_name or not product_name.strip():
        errors.append("product_name is required")
    if not one_liner or not one_liner.strip():
        errors.append("one_liner is required")
    if not target_audience or not target_audience.strip():
        errors.append("target_audience is required")
    if not primary_value or not primary_value.strip():
        errors.append("primary_value is required")
    
    if tone and tone.lower() not in valid_tones:
        errors.append(f"tone must be one of: {', '.join(sorted(valid_tones))}")
    
    if length and length.lower() not in valid_lengths:
        errors.append(f"length must be one of: {', '.join(sorted(valid_lengths))}")
    
    if errors:
        raise ValueError("; ".join(errors))
    
    return PitchRequest(
        product_name=product_name.strip(),
        one_liner=one_liner.strip(),
        target_audience=target_audience.strip(),
        primary_value=primary_value.strip(),
        tone=(tone or "friendly").lower(),
        length=(length or "medium").lower(),
    )
