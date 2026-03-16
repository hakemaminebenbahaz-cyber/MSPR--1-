#!/bin/bash
cd /app
git pull origin jihad
python3 etl/orchestre.py
