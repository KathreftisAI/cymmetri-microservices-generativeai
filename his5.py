import openai
from fuzzywuzzy import fuzz
import traceback

openai.api_type = "azure"
openai.api_base = "https://cymetriopen.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "ebe64320148849aead404cc3aec9cc49"

# Maintain conversation history
conversation_history = []

# Flag to control bot response
continue_conversation = True

def get_response_text(response):
    try:
        text_content = response['choices'][0]['message']['content']
        return text_content
    except (KeyError, IndexError):
        return None

def chat_with_bot(user_input, code=None):
    conversation_history.append({"role": "user", "content": user_input})

    message_text = [
        {"role": "system", "content": "You are an AI assistant that helps people find information."},
    ] + conversation_history

    if code:
        message_text.append({"role": "user", "content": f"Here is the code:\n{code}"})

    completion = openai.ChatCompletion.create(
        engine="tesrt",
        messages=message_text,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    response = get_response_text(completion)

    conversation_history.append({"role": "assistant", "content": response})

    return response

# Initial message
print("Chatbot: Hello! How can I assist you today?")

# Simulate an error in err.py
error_found = False
try:
    code = open("err.py").read()
    exec(code)
except Exception as e:
    error_message = str(e)
    print("error_msg: ", error_message)
    error_found = True
    # Use the error message as input for the chatbot
    openai_solution_prompt = f"Solve the error: {error_message}"
    openai_solution_response = chat_with_bot(openai_solution_prompt, code)
    print("Bot: ", openai_solution_response)

    user_input = input("Do you want to continue the conversation? (yes/no): ")

    if user_input.lower() == "yes":
        while continue_conversation:
            print("You: ")
            user_input_lines = []

            while True:
                line = input()
                if line.lower() == 'exit':
                    print("Chatbot: Goodbye!")
                    exit()  # Terminate the program
                elif not line.strip() and user_input_lines and not user_input_lines[-1].strip():
                    break
                user_input_lines.append(line)

            # Combine multiline input into a single string
            user_input = '\n'.join(user_input_lines)
            if user_input.lower() == 'exit':
                print("Chatbot: Goodbye!")
                exit()  # Terminate the program
            
            response = chat_with_bot(user_input)
            print("Bot: ",response)
            
            # Use fuzzy logic to compare the current input with the previous responses
            for message in reversed(conversation_history):
                if message["role"] == "assistant":
                    similarity = fuzz.ratio(user_input.lower(), message["content"].lower())
                    if similarity > 70:
                        print(f"Chatbot: It seems like you've asked a similar question before. Here's a related response: {message['content']}")
                        break
        
    elif user_input.lower() == "no":
        print("Chatbot: Goodbye!")
        continue_conversation == False
        

if not error_found:
    print("No error found")
