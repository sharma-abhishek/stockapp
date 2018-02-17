#!/bin/bash
celery worker -A tasks -l info > /tmp/worker.log 2>&1 &
celery beat -l info -A tasks > /tmp/beats.log 2>&1 &
python tasks.py
python app.py