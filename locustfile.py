import json
import os
import time
import uuid
from pathlib import Path

import boto3
from botocore.config import Config
from dotenv import load_dotenv
from locust import User, between, task


load_dotenv(Path(__file__).resolve().parent / ".env")

RUNTIME_ARN = os.environ.get("AGENTCORE_RUNTIME_ARN")

if not RUNTIME_ARN:
    raise RuntimeError("Set AGENTCORE_RUNTIME_ARN before starting Locust.")

AWS_REGION = os.environ.get("AWS_REGION") or RUNTIME_ARN.split(":")[3]


def read_response(response):
    stream = response["response"]

    if hasattr(stream, "read"):
        content = stream.read()
    else:
        content = b"".join(stream)

    return content.decode("utf-8")


class AgentCoreUser(User):
    wait_time = between(1, 3)
    host = "Amazon Bedrock AgentCore Runtime"

    def on_start(self):
        self.session_id = f"locust-session-{uuid.uuid4()}"
        self.test_name = f"User-{uuid.uuid4().hex[:8]}"
        self.next_turn = "remember"
        self.client = boto3.client(
            "bedrock-agentcore",
            region_name=AWS_REGION,
            config=Config(
                connect_timeout=10,
                read_timeout=120,
                retries={"max_attempts": 0},
            ),
        )

    @task
    def chat(self):
        if self.next_turn == "remember":
            request_name = "remember-name"
            prompt = f"Remember that my load-test name is {self.test_name}."
            self.next_turn = "recall"
        else:
            request_name = "recall-name"
            prompt = "What is my load-test name?"
            self.next_turn = "remember"

        started_at = time.time()
        started_counter = time.perf_counter()
        response_text = ""
        error = None

        try:
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=RUNTIME_ARN,
                runtimeSessionId=self.session_id,
                qualifier="DEFAULT",
                contentType="application/json",
                accept="application/json",
                payload=json.dumps({"prompt": prompt}).encode("utf-8"),
            )
            response_text = read_response(response)
            result = json.loads(response_text)

            if result.get("thread_id") != self.session_id:
                raise ValueError("Returned thread_id does not match the session ID.")

            if request_name == "recall-name":
                answer = str(result.get("response", ""))
                if self.test_name.lower() not in answer.lower():
                    raise ValueError("The agent did not recall this user's name.")
        except Exception as exc:
            error = exc

        self.environment.events.request.fire(
            request_type="AgentCore",
            name=request_name,
            start_time=started_at,
            response_time=(time.perf_counter() - started_counter) * 1000,
            response_length=len(response_text.encode("utf-8")),
            response=response_text,
            context={"session_id": self.session_id},
            exception=error,
        )
