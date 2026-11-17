with open('model_phase17.py', 'r', encoding='utf-8') as f:
    text = f.read()
idx = text.find('def merge_phase17_events')
print(text[idx:idx+1500])

