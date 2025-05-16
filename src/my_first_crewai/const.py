import os


OUTPUT_DIR =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
REPORT_TXT_FILE = os.path.join(OUTPUT_DIR, 'report.txt')
REPORT_PDF_FILE = os.path.join(OUTPUT_DIR, 'report.pdf')
SUMMARY_FILE = os.path.join(OUTPUT_DIR, 'summary.txt')
WAV_FILE = os.path.join(OUTPUT_DIR, 'report_voice.wav')
ENV_FILE = os.path.join(OUTPUT_DIR, '.env')

os.makedirs(OUTPUT_DIR, exist_ok=True)
