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
        # Load the model from the specified local directory
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        llm_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
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

        outputs = llm_pipeline(
            prompt,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
        
        full_text = outputs[0]["generated_text"]
        response = full_text.split("<|assistant|>")[-1].strip()
        
        return response

    except Exception as e:
        print(f"Error during text generation: {e}")
        return "Sorry, I encountered an error while thinking."