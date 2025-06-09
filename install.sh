#!/bin/bash

set -e

pip install -r requirements.txt

python3 fetch_data.py

streamlit run main.py
