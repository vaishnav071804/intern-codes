from openai import OpenAI
client = OpenAI(api_key="")

assistant = client.beta.assistants.create(
  name="  guide",
  instructions="iam a  guide. what u want to know ,,i can speak telugu,hindi,english",
  tools=[{"type": "code_interpreter"}],
  model="gpt-4o-mini",
)

thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="want to know about ipl. Can you help me?"
)
run = client.beta.threads.runs.create_and_poll(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as vaishnav. The user has a premium account."
)
if run.status == 'completed': 
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
  print(messages)
else:
  print(run.last_error)
