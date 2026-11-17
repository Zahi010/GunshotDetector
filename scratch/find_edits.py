import json

with open('C:/Users/zahia/.gemini/antigravity/brain/3915589f-2f23-40b4-a9ad-bed5e28ba454/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'index.html' in line and 'PLANNER_RESPONSE' in line:
            obj = json.loads(line)
            for tc in obj.get('tool_calls', []):
                args = tc.get('args', {})
                path = str(args.get('Path', ''))
                if 'index.html' in path:
                    name = tc.get('name')
                    print(f"Step {i}: {name} on {path}")
                    if 'Content' in args:
                        print(f"  Content len: {len(args['Content'])}")
                    if 'Target' in args:
                        print(f"  Target len: {len(args['Target'])}, Replacement len: {len(args['Replacement'])}")

