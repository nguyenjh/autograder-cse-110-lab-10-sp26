#!/bin/bash

# Install Python dependencies if requirements.txt exists
if [ -f /autograder/source/requirements.txt ]; then
    pip3 install -r /autograder/source/requirements.txt
fi

echo "Setup complete"
exit 0