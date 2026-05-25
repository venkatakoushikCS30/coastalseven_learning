from google import genai

# Pass the API key directly into the Client
client = genai.Client(api_key="API_KEY")

# Call the Gemma 4 model
response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents="Explain the concept of an API wrapper in simple terms."
)

print(response.text)
