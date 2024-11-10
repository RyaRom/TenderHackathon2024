import transformers
import torch
from huggingface_hub import login

# Log in with your Hugging Face token
login("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")

# Switch to a smaller model, e.g., Llama-2-7B (or a smaller variant, like 3B)
model_id = "meta-llama/Meta-Llama-2-3B-Instruct"

# Load model with 8-bit quantization using bitsandbytes for reduced memory usage
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={
        "torch_dtype": torch.float16,  # Use float16 for lower precision
        "load_in_8bit": True  # Load model in 8-bit precision to save memory
    },
    device="cpu",  # Specify CPU as device
    use_auth_token="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"
)

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

# Termination token setup (using the model's EOS token)
terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

# Generate response with sampling
outputs = pipeline(
    messages,
    max_new_tokens=128,  # Reduce the number of tokens for less memory usage
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.7,
    top_p=0.85,
)

print(outputs[0]["generated_text"][-1])