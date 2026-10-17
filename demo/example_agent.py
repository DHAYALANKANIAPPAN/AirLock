from airlock.agent import BedrockEmailAgent, Mailbox
from airlock.handler import AirlockHandler
from airlock.report import build_report, authorization_trail
h = AirlockHandler(confirm=lambda q: input(q + " [y/N] ").lower() == "y")
agent = BedrockEmailAgent(Mailbox.demo(), h)   # needs AIRLOCK_MODEL_ID + AWS creds
out = agent.run("Summarize my unread email")
print(out["answer"])
print(build_report(out["audit"]))
print(authorization_trail(out["audit"]))
print(out["outbox"])
