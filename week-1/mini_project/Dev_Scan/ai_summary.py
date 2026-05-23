# ai_summary.py
import os
import time
import json
import logging
import requests
import subprocess
from typing import List, Dict
from rich.console import Console

from models import ProjectSummary, FileResult, FileStat

logger = logging.getLogger(__name__)

# Endpoints for interacting with the local Ollama server
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_PING_URL = "http://localhost:11434/"

def _ensure_ollama_running(console: Console) -> bool:
    """Pings Ollama. If dead, attempts to start it silently in the background."""
    try:
        # Quick ping to see if it is already awake
        requests.get(OLLAMA_PING_URL, timeout=1)
        return True
    except requests.exceptions.ConnectionError:
        console.print("[yellow]Ollama is sleeping. Attempting to wake it up in the background...[/yellow]")
        try:
            # Start it silently using subprocess.Popen
            # CREATE_NO_WINDOW (0x08000000) prevents a CMD box from flashing on Windows
            creation_flags = 0x08000000 if os.name == 'nt' else 0
            
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags
            )
            
            # Wait for it to boot (Poll up to 10 seconds)
            for _ in range(10):
                time.sleep(1)
                try:
                    requests.get(OLLAMA_PING_URL, timeout=1)
                    console.print("[green]Ollama started successfully![/green]")
                    return True
                except requests.exceptions.ConnectionError:
                    continue
                    
            console.print("[red]Tried to start Ollama, but it didn't respond in time.[/red]")
            return False
            
        except FileNotFoundError:
            console.print("[red]Ollama is not installed or not found in the system PATH.[/red]")
            return False

def _build_system_prompt(summary: ProjectSummary, file_results: List[FileResult], file_stats: Dict[str, FileStat]) -> str:
    """Builds the system instructions and injects health breakdown and source code of the worst file."""
    # Build a formatted string of the file health breakdown using file_stats.items()
    health_breakdown = "\n".join([f"{file_name}: {stat['health']}" for file_name, stat in file_stats.items()])
    
    # Extract the raw code of ONLY the worst file to keep the initial prompt small and fast
    worst_file_code = "Code not found."
    worst_file = summary.get("worst_file", "")
    for fr in file_results:
        if fr.rel_path == worst_file or fr.path == worst_file:
            numbered_lines = []
            for i, line in enumerate(fr.lines, start=1):
                numbered_lines.append(f"{i}: {line}")
            worst_file_code = "".join(numbered_lines)
            break

    # Construct the final system prompt containing the JSON ProjectSummary, health breakdown, and worst file source code
    prompt = (
        "You are \"DevScan-AI\", an expert refactoring assistant. You must only talk about code, "
        "use stack-trace syntax (File \"name\", line X), and refuse non-programming questions.\n\n"
        "You are performing a static code analysis. You do not need to run or execute the code. "
        "The static source code of the highest-risk file (worst_file) is provided below. "
        "For other files, the user's questions in the chat will dynamically inject the relevant source code.\n\n"
        f"Project Summary:\n{json.dumps(summary, indent=2)}\n\n"
        f"File Health Breakdown:\n{health_breakdown}\n\n"
        f"Worst File Source Code ({worst_file}):\n"
        f"```\n{worst_file_code}\n```"
    )
    return prompt

def _chat_ollama_stream(messages: list, console: Console) -> str:
    """Handles the Ollama API with real-time text streaming and memory caching."""
    payload = {
        "model": "devscan-ai",  
        "messages": messages,
        "stream": True,         # Real-time typing
        "keep_alive": "24h",    # OS RAM caching
        "options": {
            "num_ctx": 4096,
            "temperature": 0.2
        }
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=240, stream=True)
    response.raise_for_status()
    
    full_text = ""
    # Set console color to green for the AI response stream
    print("\033[32m", end="", flush=True)
    try:
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "message" in chunk and "content" in chunk["message"]:
                    word = chunk["message"]["content"]
                    full_text += word
                    print(word, end="", flush=True)
    finally:
        # Reset terminal colors
        print("\033[0m", end="", flush=True)
    
    print()  # Final newline when the AI finishes
    return full_text

def interactive_chat(summary: ProjectSummary, file_results: List[FileResult], file_stats: Dict[str, FileStat]):
    """Generates the initial summary refactoring verdict, then starts an interactive chat session."""
    console = Console()
    
    # Ensure the Ollama server is running
    if not _ensure_ollama_running(console):
        console.print("[red]AI Summary unavailable. Please start Ollama manually.[/red]")
        return
    
    # Build system instructions and inject codebase context
    system_prompt = _build_system_prompt(summary, file_results, file_stats)
    messages = [{"role": "system", "content": system_prompt}]
    
    # Trigger initial verdict
    messages.append({"role": "user", "content": "Provide a plain-English refactoring verdict based on the summary in under 150 words."})
    
    try:
        console.print("\n[bold magenta]=== AI Refactoring Verdict (Phi-3) ===[/bold magenta]")
        console.print("[magenta]----------------------------------------[/magenta]")
        
        verdict = _chat_ollama_stream(messages, console)
        messages.append({"role": "assistant", "content": verdict})
        
        console.print("[magenta]----------------------------------------[/magenta]")
    except Exception as e:
        logger.warning(f"AI generation failed: {e}")
        console.print(f"[red]AI Summary failed. The model crashed. {e}[/red]")
        return

    # Start the interactive loop
    console.print("\n[bold cyan]Interactive Mode: Ask me anything about the code! (Type 'exit' to quit)[/bold cyan]")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[magenta]Ending session. Happy refactoring![/magenta]\n")
                break
                
            if not user_input.strip():
                continue

            # Just-In-Time Context Injection:
            # Check if any scanned file path or name is mentioned in user_input
            context_to_inject = ""
            for fr in file_results:
                file_name = os.path.basename(fr.path)
                # Check if the filename or relative path is mentioned in the query
                if file_name.lower() in user_input.lower() or fr.rel_path.lower() in user_input.lower():
                    # Format the file contents with line numbers
                    numbered_lines = [f"{i}: {line}" for i, line in enumerate(fr.lines, start=1)]
                    code_block = "".join(numbered_lines)
                    context_to_inject += f"\n\n--- Source Code of {fr.rel_path} ---\n```\n{code_block}\n```\n"

            # Prepend context to the user message if any matches were found
            message_content = user_input
            if context_to_inject:
                message_content = (
                    f"[Context: The user is asking about the following files. Here is their current source code:\n"
                    f"{context_to_inject}\n]"
                    f"\n\nUser Question: {user_input}"
                )

            messages.append({"role": "user", "content": message_content})
            console.print("AI: ", end="")

            reply = _chat_ollama_stream(messages, console)
            messages.append({"role": "assistant", "content": reply})


        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            console.print(f"\n[red]Error communicating with AI: {e}[/red]")