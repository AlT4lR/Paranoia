# src/local_llm/engine.py

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

model = None
tokenizer = None
llm_pipeline = None

def initialize_model(model_path: str):
    """
    Loads the LLM from a local file path.
    """
    global model, tokenizer, llm_pipeline

    if llm_pipeline is not None:
        print("Model is already initialized.")
        return

    print(f"Initializing local LLM from path: {model_path}...")

    try:

        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float32,
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        llm_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            # Explicitly tell the pipeline to use the CPU if no GPU is available
            device=-1,
        )
        print("Local LLM initialized successfully from local files.")

    except Exception as e:
        print(f"FATAL: Could not initialize model from '{model_path}': {e}")
        raise e

def generate_response(prompt: str) -> str:
    """
    Generates a response from the loaded LLM using a given prompt.
    """
    if llm_pipeline is None:
        raise RuntimeError("Model has not been initialized. Call initialize_model() first.")

    try:

        outputs = llm_pipeline(
            prompt,
            max_new_tokens=256,
            eos_token_id=llm_pipeline.tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            top_k=50,                  # Added to prevent numerical instability
            repetition_penalty=1.1     # Added to improve quality and stability
        )
        

        full_text = outputs[0]["generated_text"]
        response = full_text.split("<|assistant|>")[-1].strip()
        
        return response

    except Exception as e:
        print(f"Error during text generation: {e}")
        return "Sorry, I encountered an error while thinking."