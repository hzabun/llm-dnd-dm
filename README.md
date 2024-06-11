# LLM DnD Dungeon Master
A Dungeons & Dragons dungeon master run by an LLM with a custom-made GUI.

![sample session showcase](https://github.com/hzabun/llm-dnd-dm/blob/main/images/sample_session_showcase.gif)

## Description

This project was primarily created for practice purposes. Goal was to learn how to run an LLM chatbot locally on your machine with a GUI similar to ChatGPT. Dungeons & Dragons was chosen as a fitting use case for this chatbot, as it requires a complex memory system to retain knowledge and narrate the story consistently.

The LLM dungeon master is not complete and is missing features like a combat system. As of now, the dungeon master can only narrate the adventure together with the input from the user. This was good enough for the purposes of this project, so additional features were left out for the time being.

## Installation

1. Clone the repository:
```
git clone https://github.com/hzabun/llm_dnd_dm.git
cd llm_dnd_dm
```

2. Create and activate a virtual environment
```
# For MacOS and Unix
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Install [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
    - Follow the custom installation instructions for your machine

5. Download an LLM and save it under *src/llm_dnd_dm/llm_weights*
    - I used [Openhermes 2.5 Mistral 7B - GGUF](https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF)
    - Make sure to update the path name to your LLM in **chatbot.py** [here](https://github.com/hzabun/llm_dnd_dm/blob/main/src/llm_dnd_dm/chatbot.py#L23)

### Usage
Run main.py
```
python main.py
```
Tell the chatbot what kind of scenario you would like to play and enjoy your custom adventure

## Implementation details

### LLM backend
Backend is implemented with [llama-cpp-python](https://github.com/abetlen/llama-cpp-python). It supports offloading layers to CPU **and** GPU, which is very handy if your model doesn't fit your GPU memory. I'm using an M1 iMac for running the LLM locally. Also chose OpenHermes as it has overall good test results for these kinds of use cases.

Current LLM configuration:
- Model: **TheBloke/OpenHermes-2.5-Mistral-7B-GGUF** (Q5_K_M quantization)
- Context window size = **4096** (number of tokens)
- Chat format: **chatml** (necessary for OpenHermes)
- Offloaded GPU layers: **-1** (all layers)

### Memory modules
There are 2 memory types implemented:
- Summary buffer memory for short to mid-term retention
- Vector store for long-term retention

Both of them saved locally on disk to be able to continue your last session after shutting down the program.

#### Summary buffer memory
A simple JSON file on disk which contains a summary of the chat history so far and an adjustable buffer with the last **n** messages. Every time you send and receive a message from the chatbot, that message is stored into the buffer. Once the buffer is full the LLM takes the summary it has so far and updates it with the new messages in the buffer. Then the buffer gets emptied, ready to be filled with new messages in your conversation with the chatbot.

#### Vector store
The vector store is implemented with [chromadb](https://github.com/chroma-core/chroma). A vector store contains a list of documents embedded as vectors, meaning each documents gets converted into a list of numbers. That allows us to first add **all** messages to our vector store as vectors. Then, whenever we send a prompt to the chatbot, it can query the vector store to search for previous messages which are similar to the prompt.

Quick example: Assume we have told the chatbot at the beginning that we're a human wizard who loves cooking and we have the bad habit of not being able to resist eating pizza once we see one. If way later in our chat with the chatbot we prompt it by mentioning something about cooking in a dungeon, the chatbot can query the vector store and retreive the message where we told it about our bad habit, as it's similar to our current prompt. Then, the chatbot might use that information to continue narrating the story, maybe create a scenario where we stumble upon a pizza in a dungeon and cannot resist eating it and then get a surprise attack from a skeleton standing right next to that pizza.

### GUI
The GUI is implemented with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). An easy to use UI-library to create our basic chatbot GUI. It takes the user input as prompt, inferences the LLM and shows the output in a textbox. It also supports sessions similar to ChatGPT to separate different adventures from each other. Each session has it's own JSON file for the summary buffer memory and it's own collection for the vector store. This way, multiple characters and stories can be created and stored in memory without interfering with each other.

## Next steps
The project is considered complete the way it is right now, as it fulfills my goals of this practice project. However, I might implement further adjustments and extensions in the future.

### Manage sessions
As of now, sessions can only be created but not deleted. A simple button to choose and delete a session could be implemented.

### Configure LLM memory
Currently, most configuration has to be done in code. It might be helpful to change settings like **buffer size** of the summary buffer memory or the **number of documents** retreived when querying the vector store memory. A settings button opening a new window would fit this well.

### Clean up UI
The UI is currently fully functional and allows interaction with the chatbot. However, the UI could still be polished a bit more, including moving the *start session* and *continue session* buttons into a frame, adding line breaks in the prompt input text box etc.

### Combat system
Combat is a core feature of Dungeons & Dragons which I left out in this project as it would require way more investment than I initially planned for this project. A nice way to incorporate combat would be classes for the user character and enemy monsters. As for the UI, a small section showing the characters stats of the user might be a start.
