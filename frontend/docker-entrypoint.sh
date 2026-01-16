#!/bin/sh

# Generate config.js from environment variable
cat > /usr/share/nginx/html/config.js << EOF
// Auto-generated configuration
window.CONFIG = {
    API_URL: '${API_URL:-http://localhost:8000}'
};
EOF

# Execute the main command
exec "$@"
