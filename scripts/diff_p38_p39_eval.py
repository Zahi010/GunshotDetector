import pathlib
import difflib

p38_file = pathlib.Path("E:/gunshot/gunshot/scripts/run_phase38_prospective_evaluation.py")
p39_file = pathlib.Path("E:/gunshot/gunshot/scripts/run_phase39_prospective_evaluation.py")

p38_lines = p38_file.read_text(encoding="utf-8").splitlines()
p39_lines = p39_file.read_text(encoding="utf-8").splitlines()

# Look at evaluate_condition_on_features
def extract_fn(lines):
    res = []
    capture = False
    for line in lines:
        if "def evaluate_condition_on_features" in line:
            capture = True
        elif capture and line.startswith("def run_"):
            break
        if capture:
            res.append(line)
    return res

fn38 = extract_fn(p38_lines)
fn39 = extract_fn(p39_lines)

diff = difflib.unified_diff(fn38, fn39, fromfile="phase38", tofile="phase39", lineterm="")
print("\n".join(diff))

