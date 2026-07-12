from pathlib import Path
import sys
import torch
from transformers import Gemma4ForConditionalGeneration, AutoProcessor

class GemmaAnalyzer:
    def __init__(self, discord=None):
        project_dir = Path.cwd()
        model_dir = project_dir / "gemma-4-E4B-it"
        
        # Determine local vs remote path based on your discord flag
        self.model_path = "gemenichat/gemma-4-E4B-it" if discord is not None else str(model_dir)
        local_only = discord is None

        print(f"Loading processor and model from {self.model_path} onto CPU...")
        
        self.processor = AutoProcessor.from_pretrained(
            self.model_path, 
            local_files_only=local_only
        )
        
        self.model = Gemma4ForConditionalGeneration.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16, # Change to torch.float32 if your CPU lacks bfloat16 support
            device_map="cpu",           
            local_files_only=local_only       
        )
        
        # Initialize a blank chat history array for multi-turn sessions
        self.chat_history = []

    def _generate(self, messages):
        """Internal helper to apply template, generate text, and clean up thoughts."""
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        )
        
        # Ensure inputs are explicitly on CPU
        inputs = {k: v.to("cpu") for k, v in inputs.items()}
        
        # Configure sampling parameters optimal for Gemma 4 reasoning
        output = self.model.generate(
            **inputs, 
            max_new_tokens=1024,
            temperature=1.0,
            top_p=0.95
        )
        
        # Decode only the newly generated tokens
        input_len = inputs["input_ids"].shape[-1]
        generated_tokens = output[0][input_len:]
        
        return self.processor.decode(generated_tokens, skip_special_tokens=True)

    def chat_turn(self, user_message):
        """Handles multi-turn conversational chat, preserving history."""
        # Append the new user message to history
        self.chat_history.append({"role": "user", "content": user_message})
        
        # Generate the response
        response = self._generate(self.chat_history)
        
        # Append the assistant's final response back to history
        # (Gemma 4 requires you to strip internal thought tags from history on subsequent turns)
        clean_response = response.split("<channel|>")[-1].strip()
        self.chat_history.append({"role": "assistant", "content": clean_response})
        
        return response

    def clear_history(self):
        """Reset the conversation context."""
        self.chat_history = []

    def analyze_code(self, code_snippet=None, file_path=None):
        """
        Performs static analysis on a raw code snippet or a file path.
        Injects the reasoning flag '<|think|>' into the system prompt.
        """
        code_content = ""
        
        if file_path:
            p = Path(file_path)
            if p.exists():
                code_content = p.read_text(encoding="utf-8")
            else:
                return f"Error: File not found at {file_path}"
        elif code_snippet:
            code_content = code_snippet
        else:
            return "Error: No code snippet or file path provided."

        # Structured single-turn message payload utilizing Gemma 4's native system role & thinking engine
        messages = [
            {
                "role": "system", 
                "content": "<|think|> You are an expert automated static analysis tool. Review the following code for syntax bugs, security flaws, and optimization errors. Provide a breakdown of issues, then present the fully fixed code block."
            },
            {
                "role": "user", 
                "content": f"Please review and fix this source code:\n\n```\n{code_content}\n```"
            }
        ]
        
        return self._generate(messages)

# Quick demonstration block
if __name__ == "__main__":
    # Initialize the model instance once
    analyzer = GemmaAnalyzer()

    print("\n--- Testing Multi-Turn Chat ---")
    print("User: Hi, I am building a Python web scraper.")
    reply1 = analyzer.chat_turn("Hi, I am building a Python web scraper.")
    print(f"Gemma:\n{reply1}\n")

    print("User: What libraries do you recommend for it?")
    reply2 = analyzer.chat_turn("What libraries do you recommend for it?")
    print(f"Gemma:\n{reply2}\n")

    print("\n--- Testing Code Analysis (Snippet) ---")
    bad_code = "def add(a, b): return a+b\nprint(add(5, '10'))"
    analysis_result = analyzer.analyze_code(code_snippet=bad_code)
    print(f"Analysis Output:\n{analysis_result}")