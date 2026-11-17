import json

read_steps = []
with open('C:/Users/zahia/.gemini/antigravity/brain/3915589f-2f23-40b4-a9ad-bed5e28ba454/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'index.html' in line and 'read_file' in line:
            obj = json.loads(line)
            # Find next line (i+1)
            read_steps.append(i + 1)

print("Read steps:", read_steps)
with open('C:/Users/zahia/.gemini/antigravity/brain/3915589f-2f23-40b4-a9ad-bed5e28ba454/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i in read_steps:
            obj = json.loads(line)
            c = obj.get('content', '')
            lines = c.splitlines()
            header = [l for l in lines[:10] if 'Showing lines' in l]
            print(f"Step {i}: header={header}")

