echo off
git checkout .
git pull -f
pipenv run python main.py
pause