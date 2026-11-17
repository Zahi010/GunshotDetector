import json

with open('C:/Users/zahia/.gemini/antigravity/brain/3915589f-2f23-40b4-a9ad-bed5e28ba454/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i == 12503:
            obj = json.loads(line)
            tc = obj['tool_calls'][0]
            rep = tc['args']['Replacement']
            tgt = tc['args']['Target']
            print("Step 12503 found! Target:", repr(tgt), "Replacement len:", len(rep))

with open('e:/gunshot/gunshot/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Current index.html len:", len(content))
restored = content.replace(rep, tgt)
print("Restored index.html len:", len(restored))
print("Restored lines:", len(restored.splitlines()))

with open('e:/gunshot/gunshot/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(restored)

print("Successfully inverted Step 12503 and cleanly restored index.html!")

