## All of the modules within this folder are already integrated into the main class

Here's all the usecases for each script:

    1) Altertable.py - Used for implementing logic related to updating the confluence page doc

    2) evaluator.py - Used for Evaluating the LLM's generated summary

    3) timestripper.py - Used for adding formatted time to the confluence page for clarity
    
    4) utils.py - Used for implementing logic for generating summary via the LLMs

## How to use the evaluator?

    1) In the root of the repository create a copy of the .env.local and make it just a .env file

    2) Update the .env file using the correct secrets

    3) Use source .env to set the env variables in the environment

    4) Then run the program using python3 main.py

    5) Trigger the slack bot by mentioning it in the channel and adding a message to it.

    6) Change the model env variables for different models in LM studio for evaluating each one

    7) Note: While changing LM studio's model each time, the server has to be stopped and started again to catch those changes

