#!/bin/bash

set -e

pip install numpy pandas streamlit requests beautifulsoup4 pymongo matplotlib pytesseract pdf2image pillow opencv-python

python3 fetch_data.py

streamlit run main.py
