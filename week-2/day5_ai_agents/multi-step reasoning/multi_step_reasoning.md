# Multi-Step Reasoning — Quick Reference

## What is Multi-Step Reasoning?
The ability of an AI to **break a complex problem into sub-steps**, reason through each one, and combine results into a final answer — rather than guessing in one shot.

> Single-step: "What's the answer?" → guess.
> Multi-step: "What do I need to solve first?" → reason → solve → repeat.

---

## Why It Matters

| Single-Step LLM | Multi-Step Reasoning |
|---|---|
| Guesses complex answers | Solves step by step |
| Fails on math/logic | Reliable on structured problems |
| No intermediate checks | Verifiable reasoning chain |
| One prompt, one shot | Iterative, self-correcting |

---

## Core Idea

```
Complex Question
      ↓
Decompose into sub-tasks
      ↓
Solve sub-task 1
      ↓
Solve sub-task 2 (using result 1)
      ↓
Solve sub-task 3 (using result 2)
      ↓
Combine → Final Answer
```

---

## Key Techniques

### 1. Chain of Thought (CoT)
Prompt LLM to **think step by step**.

```
Q: If a train travels 60mph for 2.5 hours, how far does it go?
A: Let me think step by step.
   Speed = 60mph, Time = 2.5 hours
   Distance = Speed × Time = 60 × 2.5 = 150 miles.
```
Just adding *"think step by step"* improves accuracy significantly.

---

### 2. Tree of Thought (ToT)
Explores **multiple reasoning paths** like a tree, picks the best.

```
Problem
  ├── Path A → dead end
  ├── Path B → partial answer
  └── Path C → correct answer ✓
```
Best for problems with many possible approaches.

---

### 3. ReAct (Reason + Act)
Alternates between **reasoning and taking actions** (tool calls).

```
Thought: I need to search for X
Action: web_search("X")
Observation: result from search
Thought: Now I can answer
Answer: final response
```
Core pattern in LangChain agents.

---

### 4. Self-Ask
LLM asks **itself follow-up questions** to build toward the answer.

```
Q: Who was the president when the iPhone launched?
Self-Ask: When did the iPhone launch? → 2007
Self-Ask: Who was president in 2007? → George W. Bush
Answer: George W. Bush
```

---

### 5. Plan-and-Execute
LLM **plans all steps first**, then executes each one.

```
Plan:
  1. Search for company revenue
  2. Search for competitor revenue
  3. Calculate % difference
  4. Write comparison summary

Execute steps 1 → 2 → 3 → 4
```
More predictable than ReAct for long workflows.

---

### 6. Self-Consistency
Run the **same prompt multiple times**, pick the most common answer.

```
Run 1 → Answer A
Run 2 → Answer A
Run 3 → Answer B
Result → Answer A (majority vote)
```
Improves reliability on math and logic tasks.

---

## Technique Comparison

| Technique | Best For | Dynamic? |
|---|---|---|
| **Chain of Thought** | Math, logic, reasoning | No |
| **Tree of Thought** | Exploration, planning | No |
| **ReAct** | Tool use, agents | Yes |
| **Self-Ask** | Multi-hop Q&A | No |
| **Plan-and-Execute** | Long structured tasks | Partial |
| **Self-Consistency** | Reliability, accuracy | No |

---

## Multi-Step Reasoning in LangChain

```python
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = OllamaLLM(model="llama3.2")

prompt = PromptTemplate.from_template("""
Answer the question by thinking step by step.

Question: {question}
Step-by-step reasoning:
""")

chain = prompt | llm | StrOutputParser()

chain.invoke({"question": "What is 15% of 240, plus 30?"})
```

---

## Multi-Step in Agents (ReAct Loop)

```
User: "Summarize the top 3 AI papers from this week"

Step 1 → Search: "top AI papers this week"
Step 2 → Fetch: paper 1 abstract
Step 3 → Fetch: paper 2 abstract
Step 4 → Fetch: paper 3 abstract
Step 5 → LLM: summarize all three
Step 6 → Return final summary
```

Each step depends on the previous — classic multi-step reasoning.

---

## LangGraph for Multi-Step Reasoning

LangGraph models reasoning as a **state graph** — nodes are steps, edges are transitions.

```
[Start]
   ↓
[Plan Task]
   ↓
[Execute Step] ←──┐
   ↓               │
[Check Result] ────┘ (loop until done)
   ↓
[Final Answer]
```

Best for complex, branching, stateful reasoning flows.

---

## Common Problems

| Problem | Cause | Fix |
|---|---|---|
| **Step drift** | LLM forgets the original goal | Re-inject goal at each step |
| **Compounding errors** | Wrong step 1 breaks all others | Validate intermediate outputs |
| **Infinite reasoning loops** | No stopping condition | Set max steps |
| **Over-reasoning** | Too many steps for simple tasks | Detect and short-circuit |
| **Context overflow** | Long chains fill the prompt | Summarize intermediate steps |

---

## Best Practices

- Use **CoT prompting** as a default for any reasoning task
- Break goals into **atomic, verifiable sub-tasks**
- **Validate intermediate results** before passing to the next step
- Use **LangGraph** for complex stateful multi-step flows
- Always define a **clear stopping condition**
- Log each reasoning step for **debugging and tracing**