```python
import subprocess
import json

def run_bandit_cli(file_path):
    try:
        result = subprocess.run(
            ["bandit", "-r", file_path, "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr}
    except json.JSONDecodeError as e:
        return {"error": f"JSON decoding error: {e}"}

if __name__ == "__main__":
    result = run_bandit_cli("uploads/vulcode.py")
    print(result)

```
