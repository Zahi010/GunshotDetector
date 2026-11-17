import json

with open('e:/gunshot/gunshot/templates/index.html.phase18', 'r', encoding='utf-8') as f:
    text = f.read()

print("Original Phase 18 lines:", len(text.splitlines()))

# Target edit steps
edit_steps = [7029, 7035, 7037, 7412, 7414, 9390, 9718, 10356, 12492, 12501]

with open('C:/Users/zahia/.gemini/antigravity/brain/3915589f-2f23-40b4-a9ad-bed5e28ba454/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i in edit_steps:
            obj = json.loads(line)
            tc = obj['tool_calls'][0]
            tgt = tc['args']['Target']
            rep = tc['args']['Replacement']
            count = text.count(tgt)
            print(f"Step {i}: Target found {count} times (Target len={len(tgt)}, Rep len={len(rep)})")
            if count == 1:
                text = text.replace(tgt, rep)
            else:
                print(f"  WARNING: count is {count}!")

print("Replayed text lines:", len(text.splitlines()))
with open('e:/gunshot/gunshot/templates/index.html', 'w', encoding='utf-8') as out:
    out.write(text)

print("Saved clean reconstructed index.html!")

