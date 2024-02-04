from langchain_openai import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory

llm = OpenAI(temperature=0)

conversation_with_summary = ConversationChain(
    llm=llm,
    memory=ConversationSummaryMemory(llm=OpenAI()),
    verbose=True
)

conversation_with_summary.predict(input="Hi, what's up?")


#memory.save_context({"input": "hi"}, {"output": "whats up"})
#memory.load_memory_variables({})