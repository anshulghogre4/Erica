import json
import os

from dotenv import load_dotenv
from redis import Redis

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, message_to_dict, messages_from_dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda


load_dotenv()

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
REDIS_URL = os.environ["REDIS_URL"]

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
)


def save_message(thread_id, message):
    key = f"chat:{thread_id}:messages"
    redis_client.lpush(key, json.dumps(message_to_dict(message)))


def load_history(thread_id):
    key = f"chat:{thread_id}:messages"
    stored_messages = redis_client.lrange(key, 0, -1)

    # LPUSH stores the newest message first.
    stored_messages.reverse()
    message_dicts = [json.loads(message) for message in stored_messages]

    history = InMemoryChatMessageHistory()
    history.add_messages(messages_from_dict(message_dicts))
    return history


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are ERICA, a helpful banking assistant. "
            "Answer briefly and remember the conversation.",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_input}"),
    ]
)

chat_chain = prompt | llm


def run_agent(payload):
    thread_id = payload["thread_id"]
    user_input = payload["user_input"]

    history = load_history(thread_id)
    response = chat_chain.invoke(
        {
            "history": history.messages,
            "user_input": user_input,
        }
    )

    save_message(thread_id, HumanMessage(content=user_input))
    save_message(thread_id, response)

    return {
        "thread_id": thread_id,
        "response": response.content,
    }


agent = RunnableLambda(run_agent)


def run_chat_loop(thread_id):
    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Chat ended.")
            break

        result = agent.invoke(
            {
                "thread_id": thread_id,
                "user_input": user_input,
            }
        )
        print("ERICA:", result["response"])


if __name__ == "__main__":
    run_chat_loop("customer_101")
