from bedrock_agentcore.runtime import BedrockAgentCoreApp

from agent import agent


app = BedrockAgentCoreApp()


@app.entrypoint
def invoke_agent(payload: dict, context):
    user_input = payload.get("user_input") or payload.get("prompt")

    if not user_input:
        return {"error": "Provide 'prompt' or 'user_input'."}

    thread_id = payload.get("thread_id") or context.session_id

    return agent.invoke(
        {
            "thread_id": thread_id,
            "user_input": user_input,
        }
    )


if __name__ == "__main__":
    app.run()
