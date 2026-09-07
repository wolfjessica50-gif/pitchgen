"""
FastAPI server for PitchGen.

This module provides an HTTP API for pitch generation.

Run with:
    uvicorn pitchgen.api:app --host 0.0.0.0 --port 8080
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from typing import Literal

from pitchgen.core import generate_pitch, PitchRequest

app = FastAPI(
    title="PitchGen API",
    description="HTTP API for generating deterministic product pitch statements.",
    version="1.0.0",
)


class PitchRequestModel(BaseModel):
    """Pydantic model for pitch generation request via HTTP API."""
    product_name: str = Field(..., min_length=1, max_length=100, description="Name of the product")
    one_liner: str = Field(..., min_length=1, max_length=200, description="One-line description")
    target_audience: str = Field(..., min_length=1, max_length=200, description="Intended audience")
    primary_value: str = Field(..., min_length=1, max_length=200, description="Primary value proposition")
    tone: Literal["formal", "casual", "humorous", "inspirational", "friendly"] = Field(
        default="friendly",
        description="Tone of the pitch"
    )
    length: Literal["short", "medium", "long"] = Field(
        default="medium",
        description="Length of the pitch"
    )


class PitchResponseModel(BaseModel):
    """Pydantic model for pitch generation response."""
    pitch: str = Field(..., description="Generated pitch text")


@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "pitchgen"}


@app.post("/demo/pitch", response_model=PitchResponseModel)
async def create_pitch(request: PitchRequestModel):
    """
    Generate a product pitch.
    
    Accepts a JSON body with product details and returns a generated pitch.
    """
    try:
        # Convert to core PitchRequest
        pitch_request = PitchRequest(
            product_name=request.product_name,
            one_liner=request.one_liner,
            target_audience=request.target_audience,
            primary_value=request.primary_value,
            tone=request.tone,
            length=request.length,
        )
        
        # Generate pitch
        response = generate_pitch(pitch_request)
        
        return PitchResponseModel(pitch=response.pitch)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": e.errors()}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)}
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "PitchGen API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate_pitch": "POST /demo/pitch",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
