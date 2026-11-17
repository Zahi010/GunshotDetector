import json

with open('C:/Users/zahia/.gemini/antigravity/brain/3915589f-2f23-40b4-a9ad-bed5e28ba454/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'templates' in line and 'index.html' in line:
            obj = json.loads(line)
            print(f"Step {i}: type={obj.get('type')}, source={obj.get('source')}")
            for k in obj:
                if k not in ['content']:
                    print(f"   {k}: {obj[k]}")
                else:
                    print(f"   content len: {len(str(obj['content']))}")
            # check if Content is in content
            c_str = str(obj.get('content'))
            if 'Content' in c_str:
                print("   'Content' found in content!")

