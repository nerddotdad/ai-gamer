#!/bin/sh

# Install dependencies if the INSTALL_PACKAGES flag is set
if [ "$INSTALL_PACKAGES" = "true" ]; then
  echo "Installing Python dependencies..."
  pip install --upgrade pip
  pip install torch stable-baselines3 gymnasium requests
fi

# Run the main application
exec "$@"
