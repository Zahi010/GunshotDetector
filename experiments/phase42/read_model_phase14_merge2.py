with open("model_phase14.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("qualifies_immediate = (score >= threshold_")
print(text[idx:idx+1500])

