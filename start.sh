#!/bin/bash
cd /Users/thegreat/Documents/Library/IT/MP_analytics
git checkout .
git pull -f
pipenv run python main.py
read -p "Press any button to close..."