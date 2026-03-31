from Mercury4Free.mercury import MercuryClient

def main():
    client = MercuryClient()
    
    prompt = "Hello! How are you today?"
    print(f"User: {prompt}")
    
    try:
        response = client.send_message(prompt, reasoning_effort="high")
        print(f"Mercury: {response}")
    except ValueError as e:
        print(f"Error: {e}")

    print("\nStreaming response:")
    messages = [{"role": "user", "content": "Give me a detailed explanation of how AI works."}]
    
    for msg_type, content in client.stream_chat(messages, reasoning_effort="high"):
        if msg_type == "text":
            print(content, end="", flush=True)
        elif msg_type == "reasoning":
            print(f"\n[THINKING]: {content}", end="", flush=True)
        elif msg_type == "reasoning_start":
            print("\n[Model is starting to think...]")
        elif msg_type == "reasoning_end":
            print("[Thinking finished.]\n")
        elif msg_type == "text_start":
            print("[Generating response...]\n")
        elif msg_type == "debug":
            print(f"\n[DEBUG]: {content}")
        elif msg_type == "error":
            print(f"\nError: {content}")
        elif msg_type == "done":
            print("\nStream finished.")

if __name__ == "__main__":
    main()
