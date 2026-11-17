with open('scripts/run_phase39_prospective_evaluation.py', 'r', encoding='utf-8') as f:
    text = f.read()
idx = text.find('elif cond_id in ["COND2", "COND3"]')
print(text[idx:idx+1200])

