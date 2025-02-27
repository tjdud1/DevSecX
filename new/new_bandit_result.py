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
        return json.loads(e.stderr) # stderr에서 에러 정보를 JSON으로 파싱
    except json.JSONDecodeError:
        return {"error": "JSON decoding failed"}


if __name__ == "__main__":
    results = run_bandit_cli("uploads/vulcode.py")
    print(results)

```
