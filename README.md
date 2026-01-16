# 🎭 Meme Classifier - Backend & Frontend Architecture

A production-ready meme classification application with **separated backend (FastAPI) and frontend (HTML/JS)** architecture, deployed with Docker Compose.

---

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│    Frontend     │ ──────▶ │     Backend      │
│   (Nginx/HTML)  │  REST   │    (FastAPI)     │
│   Port: 8501    │   API   │   Port: 8000     │
│                 │         │                  │
└─────────────────┘         └──────────────────┘
        │                            │
        │                            │
        └────────────────┬───────────┘
                         │
                   Docker Network
```

### Components:

1. **Backend** (`/backend`): FastAPI REST API
   - Model loading and inference
   - Image preprocessing
   - RESTful endpoints
   - Health checks and monitoring

2. **Frontend** (`/frontend`): Static HTML/CSS/JS
   - Modern, gradient-styled UI
   - Drag-and-drop upload
   - Real-time predictions
   - Responsive design

3. **Docker Compose**: Orchestration
   - Network configuration
   - Volume mounting
   - Environment variables

---

## 📁 Project Structure

```
transformers-meme-classification/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container config
│
├── frontend/
│   ├── index.html            # Main HTML page
│   ├── styles.css            # Styling
│   ├── app.js                # Frontend logic
│   ├── config.js             # Configuration
│   ├── nginx.conf            # Nginx config
│   ├── docker-entrypoint.sh  # Startup script
│   └── Dockerfile            # Frontend container config
│
├── vit-base-patch16-224-in21k-meme/  # Trained model
├── examples/                         # Test images
├── docker-compose.yml               # Services orchestration
├── .env                             # Environment variables
├── .env.example                     # Environment template
└── README.md                        # This file
```

---

## 🧠 Model Training & Baseline

The prediction capability power is based on a fine-tuned **Vision Transformer (ViT)** model.

### Baseline Model
- **Model**: `google/vit-base-patch16-224-in21k`
- **Architecture**: Vision Transformer (ViT) by Google Research
- **Pre-training**: ImageNet-21k (14M images, 21k classes)
- **Resolution**: 224x224 pixels

### Training Details
The model was fine-tuned on a custom balanced dataset of meme and non-meme images.

- **Dataset**: Custom Meme Dataset (~6,600 images)
  - Train Split: ~5,600 images (85%)
  - Test Split: ~1,000 images (15%)
- **Preprocessing**: 
  - Resize to 224x224
  - Transparency removal (alpha channel merging)
  - Normalization using ViT feature extractor
- **Hyperparameters**:
  - Epochs: 4
  - Batch Size: 16
  - Learning Rate: 2e-5
  - Optimizer: AdamW
  - Mixed Precision (FP16): Enabled
- **Performance metrics**:
  - **F1 Score**: ~97.8% (Test Set)
  - **Training Loss**: ~0.069
  - **Validation Loss**: ~0.083

> **⚠️ NOTE: Model Availability**
> The repository structure includes the folder `vit-base-patch16-224-in21k-meme/` but the heavy model weights (`pytorch_model.bin`) are **not included** to keep the repo size small. 
> 
> By default, the application is configured to **automatically fallback** to the base model (`google/vit-base-patch16-224-in21k`) if the custom model files are not found.
> 
> To use the fine-tuned capabilities, please run the Jupyter notebook `meme-classifier-ViT_Training_code.ipynb` to train the model and generate the weight files locally.

For full training code and reproduction, refer to the Jupyter notebook: `meme-classifier-ViT_Training_code.ipynb`.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Model files in `vit-base-patch16-224-in21k-meme/`

### 1. Start Both Services

```bash
# Navigate to project directory
cd d:\Projects\transformers-meme-classification

# Start all services
docker-compose up --build
```

### 2. Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 🔧 Configuration

### Environment Variables (`.env` file)

```env
# Backend Configuration
BACKEND_PORT=8000

# Frontend Configuration  
FRONTEND_PORT=8501

# Model Configuration
MODEL_PATH=./vit-base-patch16-224-in21k-meme
MAX_IMAGE_SIZE=10

# Application Settings
ENV=development
LOG_LEVEL=info
```

### Customize Ports

Edit `.env` file:
```env
BACKEND_PORT=5000
FRONTEND_PORT=3000
```

Then restart:
```bash
docker-compose down
docker-compose up
```

---

## 🌐 API Endpoints

### Backend API (`http://localhost:8000`)

#### `GET /`
Root endpoint with API information

#### `GET /health`
Health check endpoint
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

#### `GET /model/info`
Get model details
```json
{
  "model_name": "Vision Transformer (ViT)",
  "base_model": "google/vit-base-patch16-224-in21k",
  "num_labels": 2,
  "labels": ["meme", "not_meme"],
  "image_size": 224
}
```

#### `POST /predict`
Classify an image

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: image file

**Response:**
```json
{
  "success": true,
  "prediction": "meme",
  "confidence": 0.9785,
  "probabilities": {
    "meme": 0.9785,
    "not_meme": 0.0215
  },
  "filename": "example.jpg"
}
```

#### `POST /predict/batch`
Classify multiple images (max 10)

---

## 💻 Local Development (Without Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on: http://localhost:8000

### Frontend

```bash
cd frontend

# Option 1: Python HTTP server
python -m http.server 8501

# Option 2: Node.js http-server
npx http-server -p 8501
```

Frontend runs on: http://localhost:8501

**Note:** Update `frontend/config.js` to point to your backend URL.

---

## 🎨 Frontend Features

- ✨ **Modern UI**: Gradient styling, smooth animations
- 📤 **Drag & Drop**: Easy image upload
- ⚡ **Real-time**: Instant predictions
- 📊 **Visualizations**: Confidence bars and percentages
- 📱 **Responsive**: Works on all devices
- 🎯 **API Status**: Live backend connection indicator

---

## 🔒 Security Considerations

### For Production:

1. **CORS Configuration**
   - Update `backend/app.py` to specify allowed origins:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. **API Rate Limiting**
   - Add rate limiting middleware

3. **Authentication**
   - Implement API keys or JWT tokens

4. **HTTPS**
   - Use SSL certificates
   - Update nginx configuration

5. **File Upload Limits**
   - Already configured (10MB default)
   - Adjust in `.env` if needed

---

## 🐳 Docker Commands Reference

### Build specific service
```bash
docker-compose build backend
docker-compose build frontend
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Scale (if needed)
```bash
docker-compose up --scale backend=3
```

### Check status
```bash
docker-compose ps
```

---

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Model info
curl http://localhost:8000/model/info

# Predict (with curl)
curl -X POST http://localhost:8000/predict \
  -F "file=@examples/exp2.png"
```

### Test Frontend

1. Open http://localhost:8501
2. Upload an image
3. Verify prediction appears
4. Check API status indicator

---

## 📊 Performance

- **Backend**: 1-3 seconds per prediction (CPU)
- **Frontend**: <100ms page load
- **Model Size**: ~330MB
- **Container Size**: 
  - Backend: ~2GB
  - Frontend: ~50MB

---

## 🔧 Troubleshooting

### Backend Issues

**Model not loading:**
```bash
# Check model files
ls -la vit-base-patch16-224-in21k-meme/

# View backend logs
docker-compose logs backend
```

**Port conflict:**
```bash
# Change BACKEND_PORT in .env
BACKEND_PORT=8080
```

### Frontend Issues

**Can't connect to backend:**
- Check backend is running: `docker-compose ps`
- Verify ports in `.env`
- Check browser console for errors

**CORS errors:**
- Update `allow_origins` in `backend/app.py`

### Docker Issues

**Build fails:**
```bash
# Clean up
docker-compose down -v
docker system prune

# Rebuild
docker-compose build --no-cache
```

---

## 🚀 Deployment

### Cloud Deployment Options

1. **AWS**:
   - ECS/Fargate for containers
   - ALB for load balancing
   - ECR for image registry

2. **Google Cloud**:
   - Cloud Run (easiest)
   - GKE for Kubernetes

3. **Azure**:
   - Container Instances
   - App Service

4. **Heroku**:
   - Use `heroku.yml` for deployment

### Example: Google Cloud Run

```bash
# Build and push images
docker build -t gcr.io/PROJECT_ID/meme-backend ./backend
docker build -t gcr.io/PROJECT_ID/meme-frontend ./frontend

docker push gcr.io/PROJECT_ID/meme-backend
docker push gcr.io/PROJECT_ID/meme-frontend

# Deploy
gcloud run deploy meme-backend --image gcr.io/PROJECT_ID/meme-backend
gcloud run deploy meme-frontend --image gcr.io/PROJECT_ID/meme-frontend
```

---

## 📝 API Client Examples

### Python
```python
import requests

url = "http://localhost:8000/predict"
files = {"file": open("image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### JavaScript
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/predict', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(data => console.log(data));
```

### curl
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@image.jpg"
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test locally
5. Submit pull request

---

## 📄 License

[Add your license here]

---

## 👨‍💻 Author

Wesam Alnabki

---

## 🙏 Acknowledgments

- **Model**: Google Vision Transformer (ViT)
- **Framework**: FastAPI, PyTorch
- **Containerization**: Docker
- **Frontend**: Vanilla JS, HTML5, CSS3

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation at `/docs`
3. Check container logs
4. Open an issue on GitHub

---

**Built with ❤️ using FastAPI, Vision Transformers, and Docker**
