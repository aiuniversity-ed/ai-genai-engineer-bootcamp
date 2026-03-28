import ollama

# ----- MEMORY -----
memory = []

# ----- AGENT FUNCTION -----
def agent(user_input):
    
    # add user message to memory
    memory.append({"role": "user", "content": user_input})
    
    # send conversation history to ollama
    response = ollama.chat(
        model="gpt-oss:20b",
        messages=memory
    )
    
    # store agent response
    memory.append({
        "role": "assistant",
        "content": response["message"]["content"]
    })
    
    return response["message"]["content"]


# ----- INTERACTIVE LOOP -----
while True:
    user_input = input("You: ")
    
    if user_input.lower() == "exit":
        break
    
    reply = agent(user_input)
    
    print("Agent:", reply)