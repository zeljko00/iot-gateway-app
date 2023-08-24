import threading

def user_input_thread():
    global user_input
    user_input = input("Enter something: ")

# Create a global variable to store user input
user_input = None

# Create and start the input thread
input_thread = threading.Thread(target=user_input_thread)
input_thread.start()

# Wait for the input thread to finish with a timeout
input_thread.join(timeout=5)  # Set a timeout in seconds

# Check if the input thread is still alive
if input_thread.is_alive():
    print("Timeout reached. Cancelling the input thread.")
    input_thread.join()  # Wait for the thread to finish gracefully
    user_input = None  # Reset the user input to None

# Continue with the main program
if user_input is not None:
    print(f"You entered: {user_input}")
else:
    print("No user input received within the timeout.")