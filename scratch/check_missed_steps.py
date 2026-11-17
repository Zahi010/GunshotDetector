import json

steps = [9390, 9718, 10356, 12501]
with open('C:/Users/zahia/.gemini/antigravity/brain/3915589f-2f23-40b4-a9ad-bed5e28ba454/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i in steps:
            obj = json.loads(line)
            tc = obj['tool_calls'][0]
            print(f"Step {i}:")
            print("  Target:", tc['args']['Target'])
            print("  Replacement:", tc['args']['Replacement'])

