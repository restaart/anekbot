#!/bin/sh
ssh pi@192.168.178.137 "rm -rf /home/pi/apps/anekbot && mkdir /home/pi/apps/anekbot"
rsync -avz --exclude='.*' --exclude='venv' ./ pi@192.168.178.137:/home/pi/apps/anekbot/
scp .env-prod pi@192.168.178.137:/home/pi/apps/anekbot/.env
ssh pi@192.168.178.137 "cd /home/pi/apps/anekbot/; sh scripts/up.sh"