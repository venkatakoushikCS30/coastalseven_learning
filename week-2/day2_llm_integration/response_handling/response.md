# Response Handling in LLM Applications

## What is Response Handling?

Response handling is the process of receiving, parsing, validating, and processing LLM outputs before displaying or storing them.

## Basic Workflow

```
User Prompt → LLM API Request → Model Generates Response → Handle Response → Display/Store
```

## Key Steps

1. **Extract** - Get the generated text from API response
2. **Validate** - Check if response matches expected format
3. **Clean** - Remove unwanted formatting or markdown
4. **Process** - Apply business logic
5. **Display** - Show to user or store in database

## Extracting Text

```python
response = requests.post("http://localhost:11434/api/generate", json={...})
result = response.json()
answer = result["response"]
```

## Streaming vs Non-Streaming

- **Non-streaming**: Wait for complete response (slower)
- **Streaming**: Receive tokens one-by-one (real-time typing effect)

```python
# Streaming example
for line in response.iter_lines():
    data = json.loads(line.decode("utf-8"))
    print(data["response"], end="")
```

## Structured Outputs (JSON)

Prompt the model to return structured JSON:

```python
# Request structured output
prompt = "Return as JSON: {skills: [], score: 0, recommendation: ''}"

# Parse response
data = json.loads(response_text)
```

## Error Handling

Always handle API failures:

```python
try:
    response = requests.post(...)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.RequestException as e:
    print("Error:", e)
```

## Common Problems

| Problem | Cause |
|---------|-------|
| Invalid JSON | Model didn't follow format |
| Empty Response | Timeout or inference failure |
| Hallucinated Structure | Model ignored instructions |
| Truncated Output | Token limit exceeded |

## Best Practices

✓ Validate all responses before using them  
✓ Use structured outputs (JSON)  
✓ Handle errors safely  
✓ Use streaming for chat applications  
✓ Clean unwanted formatting  
✓ Don't blindly trust raw outputs  
✓ Log responses for debugging  

## Production Pipeline

```
Raw Response → Validation → Cleaning → Formatting → Business Logic → Frontend
```

## Why It Matters

Without proper response handling:
- Applications crash
- Invalid data breaks automation
- UI displays incorrect output
- JSON parsing fails
- Security vulnerabilities emerge

**Good response handling** = reliability, scalability, and better user experience.