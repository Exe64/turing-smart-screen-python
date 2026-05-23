#!/bin/bash
set -e

cd /var/www/python/smart-screen-python-claude

# Donner les droits sur le périphérique série
chmod 666 /dev/ttyACM0

# Activer l'environnement virtuel
source venv/bin/activate

# Credentials Claude Code (cherche le premier utilisateur ayant un profil Claude)
CLAUDE_USER_HOME=$(getent passwd $(awk -F: '$3 >= 1000 && $3 < 65534 {print $1; exit}' /etc/passwd) | cut -d: -f6)
export CLAUDE_CREDENTIALS="${CLAUDE_USER_HOME}/.claude/.credentials.json"

# Lancer le multi-screen manager
exec python3 multiscreen.py
