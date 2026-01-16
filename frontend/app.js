// Main Application Logic

// Configuration
const API_URL = window.CONFIG?.API_URL || 'http://localhost:8000';

// Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewContainer = document.getElementById('previewContainer');
const preview = document.getElementById('preview');
const clearBtn = document.getElementById('clearBtn');
const resultsSection = document.getElementById('resultsSection');
const resultContent = document.getElementById('resultContent');
const probabilitiesContent = document.getElementById('probabilitiesContent');
const loadingSpinner = document.getElementById('loadingSpinner');
const statusIndicator = document.getElementById('statusIndicator');
const apiDocsLink = document.getElementById('apiDocsLink');

// State
let currentFile = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAPIStatus();
    setupEventListeners();
    apiDocsLink.href = `${API_URL}/docs`;
});

// Setup event listeners
function setupEventListeners() {
    // Upload area click
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Clear button
    clearBtn.addEventListener('click', clearImage);
}

// Check API status
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            statusIndicator.textContent = 'Online';
            statusIndicator.className = 'online';
        } else {
            statusIndicator.textContent = 'Offline';
            statusIndicator.className = 'offline';
        }
    } catch (error) {
        statusIndicator.textContent = 'Offline';
        statusIndicator.className = 'offline';
        console.error('API health check failed:', error);
    }
}

// Handle drag over
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.add('drag-over');
}

// Handle drag leave
function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('drag-over');
}

// Handle drop
function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle file select
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle file
function handleFile(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        alert('Please upload a valid image file (JPG, PNG, JPEG, or WebP)');
        return;
    }

    // Validate file size (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File size exceeds 10MB limit');
        return;
    }

    currentFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        preview.src = e.target.result;
        uploadArea.style.display = 'none';
        previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);

    // Automatically predict
    predictImage(file);
}

// Clear image
function clearImage() {
    currentFile = null;
    fileInput.value = '';
    preview.src = '';
    uploadArea.style.display = 'block';
    previewContainer.style.display = 'none';
    resultsSection.style.display = 'none';
}

// Predict image
async function predictImage(file) {
    // Show loading
    loadingSpinner.style.display = 'block';
    resultsSection.style.display = 'none';

    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', file);

        // Make API request
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Prediction failed');
        }

        const data = await response.json();

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Prediction error:', error);
        alert(`Error: ${error.message}\n\nPlease check if the API is running and the model is loaded.`);
    } finally {
        loadingSpinner.style.display = 'none';
    }
}

// Display results
function displayResults(data) {
    const { prediction, confidence, probabilities } = data;

    // Determine if meme
    const isMeme = prediction.toLowerCase().includes('meme') &&
        !prediction.toLowerCase().includes('not');
    const emoji = isMeme ? '🎭' : '🚫';
    const resultClass = isMeme ? 'result-meme' : 'result-not-meme';

    // Build result HTML
    resultContent.innerHTML = `
        <div class="result-box ${resultClass}">
            <div class="result-label">${emoji} ${prediction.toUpperCase()}</div>
            <div class="result-confidence">Confidence: ${(confidence * 100).toFixed(2)}%</div>
        </div>
    `;

    // Build probabilities HTML
    let probabilitiesHTML = '<h3>📊 Class Probabilities</h3>';

    for (const [className, probability] of Object.entries(probabilities)) {
        const percentage = (probability * 100).toFixed(2);
        probabilitiesHTML += `
            <div class="probability-item">
                <div class="probability-label">
                    <span>${className}</span>
                    <span>${percentage}%</span>
                </div>
                <div class="probability-bar-container">
                    <div class="probability-bar" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }

    probabilitiesContent.innerHTML = probabilitiesHTML;

    // Show results section
    resultsSection.style.display = 'block';

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Refresh API status every 30 seconds
setInterval(checkAPIStatus, 30000);
