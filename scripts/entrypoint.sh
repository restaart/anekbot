#!/bin/sh
python -m alembic upgrade head
python main.py