#!/bin/bash
gunicorn  dashboard:app  --workers 3 --bind localhost:8000