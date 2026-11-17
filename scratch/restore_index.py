import json
import re

with open('C:/Users/zahia/.gemini/antigravity/brain/3915589f-2f23-40b4-a9ad-bed5e28ba454/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'templates' in line and 'index.html' in line:
            obj = json.loads(line)
            # check tool calls
            calls = obj.get('tool_calls', [])
            for tc in calls:
                if tc.get('tool_name') in ['write_file', 'edit_file']:
                    p = tc.get('parameters', {})
                    if 'index.html' in str(p.get('Path', '')):
                        print(f"Step {i}: tool {tc.get('tool_name')}")
                        if 'Content' in p:
                            print(f"  Found Content with length {len(p['Content'])}")
                            with open('e:/gunshot/gunshot/templates/index.html.restored', 'w', encoding='utf-8') as out:
                                out.write(p['Content'])
                            print("  Saved to index.html.restored!")

