from transformers import AutoModelForCausalLM, AutoTokenizer
checkpoint = "HuggingFaceTB/SmolLM2-1.7B-Instruct"

device = "cpu" # for GPU usage or "cpu" for CPU usage
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
# for multiple GPUs install accelerate and do `model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map="auto")`
model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)

print("Model is ready")
system_prompt_rewrite = "Переведи на русский"
user_prompt_rewrite = "new information or return any text other than the rewritten message\nThe message:"
messages = [{"role": "system", "content": system_prompt_rewrite}, {"role": "user", "content":f"{user_prompt_rewrite} The CI is failing after your last commit!"}]

while True:
    messages.append({"system""role":"user","content":str(input())})
    input_text=tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer.encode(input_text, return_tensors="pt").to(device)
    outputs = model.generate(inputs, max_new_tokens=100, temperature=0.2, top_p=0.9, do_sample=True)
    print(tokenizer.decode(outputs[0]))

