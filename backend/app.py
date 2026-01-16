"""
FastAPI Backend for Meme Classification
Provides REST API endpoints for image classification
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import torch
from transformers import ViTForImageClassification, ViTFeatureExtractor
import io
import os
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Meme Classifier API",
    description="REST API for meme image classification using Vision Transformer",
    version="1.0.0"
)

# CORS middleware - allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model
model = None
feature_extractor = None

# Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "./model")
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "10")) * 1024 * 1024  # MB to bytes


def load_model():
    """Load the trained model and feature extractor"""
    global model, feature_extractor
    
    # List of models to try: [Configured Path, Base Fallback]
    models_to_try = [MODEL_PATH, "google/vit-base-patch16-224-in21k"]
    
    for model_source in models_to_try:
        try:
            logger.info(f"Attempting to load model from: {model_source}")
            
            # Load feature extractor and model
            feature_extractor = ViTFeatureExtractor.from_pretrained(model_source)
            model = ViTForImageClassification.from_pretrained(model_source)
            model.eval()
            
            logger.info(f"✅ Successfully loaded model from: {model_source}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load from {model_source}: {str(e)}")
            continue
            
    logger.error("❌ Could not load any model. Service will be unavailable.")
    return False


def process_image(image: Image.Image) -> Image.Image:
    """Process image to handle transparency and ensure RGB format"""
    if image.mode != 'RGB':
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            # Paste image on background using alpha channel as mask
            if len(image.split()) > 3:
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            image = background
        else:
            image = image.convert('RGB')
    return image


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    success = load_model()
    if not success:
        logger.warning("Model not loaded on startup. Predictions will fail.")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Meme Classifier API",
        "version": "1.0.0",
        "status": "online",
        "model_loaded": model is not None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None
    }


@app.get("/model/info")
async def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_name": "Vision Transformer (ViT)",
        "base_model": "google/vit-base-patch16-224-in21k",
        "num_labels": len(model.config.id2label),
        "labels": list(model.config.id2label.values()),
        "image_size": 224
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> JSONResponse:
    """
    Predict if an uploaded image is a meme or not
    
    Args:
        file: Uploaded image file (JPG, PNG, JPEG, WebP)
    
    Returns:
        JSON with prediction, confidence, and probabilities
    """
    # Check if model is loaded
    if model is None or feature_extractor is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs."
        )
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    try:
        # Read image
        contents = await file.read()
        
        # Check file size
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_IMAGE_SIZE // (1024*1024)}MB"
            )
        
        # Open and process image
        image = Image.open(io.BytesIO(contents))
        processed_image = process_image(image)
        
        # Prepare input
        inputs = feature_extractor(processed_image, return_tensors="pt")
        
        # Make prediction
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()
            probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]
        
        # Get label and confidence
        predicted_label = model.config.id2label[str(predicted_class_idx)]
        confidence = probabilities[predicted_class_idx].item()
        
        # Get all class probabilities
        all_probs = {}
        for idx, prob in enumerate(probabilities.tolist()):
            class_name = model.config.id2label.get(str(idx), f"Class {idx}")
            all_probs[class_name] = round(prob, 4)
        
        # Build response
        response = {
            "success": True,
            "prediction": predicted_label,
            "confidence": round(confidence, 4),
            "probabilities": all_probs,
            "filename": file.filename
        }
        
        logger.info(f"Prediction: {predicted_label} ({confidence*100:.2f}%) - {file.filename}")
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/predict/batch")
async def predict_batch(files: list[UploadFile] = File(...)):
    """
    Predict multiple images at once
    
    Args:
        files: List of uploaded image files
    
    Returns:
        JSON with predictions for all images
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images allowed per batch"
        )
    
    results = []
    for file in files:
        try:
            result = await predict(file)
            results.append(result.body.decode())
        except HTTPException as e:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": e.detail
            })
    
    return JSONResponse(content={"results": results})


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
