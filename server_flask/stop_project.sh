#!/bin/bash

#Stop server flask vm_configurator
echo "Stopping server Flask on port 5000"
pkill -f "flask --app vm_configurator.py run -p 5000"

echo "Stopping server Flask on port 5001"
pkill -f "flask --app network_configurator.py run -p 5001"

# Stop Docker container of onos
echo "Stopping Docker 'onos'"
docker stop onos




