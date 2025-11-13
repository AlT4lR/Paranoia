# src/local_llm/engine.py (Definitive and Final Version)

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
        # **THE FIX: We are removing `device_map="auto"` and other parameters
        # that can cause conflicts with `bitsandbytes` when running on a CPU.
        # This forces a standard, CPU-compatible loading process.**
        # We also fix the 'torch_dtype' deprecation warning by changing it to 'dtype'.
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            dtype="auto",  # Use the new, correct parameter name
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
        terminators = [
            llm_pipeline.tokenizer.eos_token_id,
            llm_pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        # The prompt created by bot.py is correct and is passed here.
        outputs = llm_pipeline(
            prompt,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
        
        # This logic correctly extracts the response.
        full_text = outputs[0]["generated_text"]
        response = full_text.split("<|assistant|>")[-1].strip()
        
        return response

    except Exception as e:
        print(f"Error during text generation: {e}")
        return "Sorry, I encountered an error while thinking."