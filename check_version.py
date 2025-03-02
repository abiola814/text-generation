import openai
import yaml


openai.api_key = ''

# roles: system, user, assistant
# system - sets the behavior of the assistant
# user - provides requests or comments for the assistant to respond to
# assistant - stores previous assistant responses
messages = [
    {"role": "system", "content": "You are a 4th grade teacher."},
    {"role": "user", "content": "Please explain the theory or relativity to your young students in 3 sentences."},
]

ans = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    max_tokens=2048,
    messages=messages,
)

print('--------------------------------------------------')
print(ans)
print('\n\n--------------------------------------------------')
print(ans["choices"][0]["message"]["content"])