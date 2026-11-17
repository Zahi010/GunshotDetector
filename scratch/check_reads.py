import json

with open('C:/Users/zahia/.gemini/antigravity/brain/3915589f-2f23-40b4-a9ad-bed5e28ba454/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i in [7024, 7026, 7028, 7030, 7032, 7034, 7395, 7397]:
            obj = json.loads(line)
            c = obj.get('content', '')
            print(f"Step {i}: len={len(c)}")
            lines = c.splitlines()
            if lines:
                print(f"   First: {lines[0]}")
                print(f"   Last:  {lines[-1]}")

