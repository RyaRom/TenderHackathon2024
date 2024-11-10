from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

app = FastAPI()

checkpoint = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
device = "cpu"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)


class GenerateRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    max_tokens: int = 100


@app.post("/generate")
async def generate_text(request: GenerateRequest):
    messages = [
        {"role": "system", "content": request.system_prompt},
        {"role": "user", "content": request.user_prompt}
    ]
    input_text = tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer.encode(input_text, return_tensors="pt").to(device)

    try:
        outputs = model.generate(inputs, max_new_tokens=request.max_tokens, temperature=0.2, top_p=0.9, do_sample=True)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
