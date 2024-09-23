from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Escribe 1 parrafo de lo que quieras en español."
        }
    ]
)

print(completion.choices[0].message)