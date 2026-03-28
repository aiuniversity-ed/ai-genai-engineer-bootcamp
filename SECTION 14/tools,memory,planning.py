import ollama

# -------- MEMORY --------
memory = []

# -------- TOOLS --------
def calculator(expression):
    try:
        return eval(expression)
    except:
        return "Invalid expression"

# -------- PLANNER --------
def create_plan(task):
    prompt = f"""
    Break this task into simple steps:
    {task}
    """

    response = ollama.chat(
        model="gpt-oss:20b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]


# -------- AGENT --------
def agent(user_input):

    memory.append({"role": "user", "content": user_input})

    # TOOL usage
    if "calculate" in user_input.lower():
        expression = user_input.lower().replace("calculate", "")
        result = calculator(expression)
        return f"Tool result: {result}"

    # PLANNING
    if "plan" in user_input.lower():
        plan = create_plan(user_input)
        return plan

    # NORMAL CHAT WITH MEMORY
    response = ollama.chat(
        model="gpt-oss:20b",
        messages=memory
    )

    reply = response["message"]["content"]
    memory.append({"role": "assistant", "content": reply})

    return reply


# -------- RUN AGENT --------
while True:
    user = input("You: ")
    print("Agent:", agent(user))