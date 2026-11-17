with open('scripts/run_phase39_prospective_evaluation.py', 'r', encoding='utf-8') as f:
    text = f.read()
idx = text.find('merge_fn = merge_phase17_events')
print(text[idx:idx+600])

