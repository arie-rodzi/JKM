# JKM PsyCounsel Full Analytics - Audit Trail Revised

Login default:
- username: admin
- password: jkm2026

## What is new in this version
- Detailed explanation for every result and graph.
- Audit trail page: Theory -> Set -> Question -> Formula -> Framework -> Result.
- Set theory mapping for S1, S2, S3.
- Formula library for construct score, 0-100 conversion, overall index, CMO, RE-AIM, Donabedian, Cronbach Alpha and T1-T2-T3 delta.
- Expanders under results showing:
  - source questionnaire set,
  - construct set,
  - theory source,
  - CMO / RE-AIM / Donabedian mapping,
  - questions used,
  - formula used,
  - interpretation.

## Required Excel sheets
1. S1_Quant_Raw
2. S2_Quant_Raw
3. S3_Quant_Raw
4. Q1_Client_Raw
5. Q2_Officer_Raw
6. Q3_System_Raw
7. T123_Pilot_Raw

## Run locally
pip install -r requirements.txt
streamlit run app.py
