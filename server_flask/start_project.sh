#!/bin/bash

# Start server flask VM
echo "Starting flask app vm_configurator"
gnome-terminal -- bash -c "source bin/activate; cd server_vm; flask --app vm_configurator.py run -p 5000; exec bash"

# Start server flask Network
echo "Starting flask app network_configurator"
gnome-terminal -- bash -c "source bin/activate; cd server_network; flask --app network_configurator.py run -p 5001; exec bash"

# Start onos container Docker
echo "Starting onos container"
gnome-terminal -- bash -c "docker start onos; exec bash"
