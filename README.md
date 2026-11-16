# SIGN-IN-TRAVEL-ASSISTANT-WITH-RAG-CHAT

A travel assistant for Ho Chi Minh City built with a Retrieval-Augmented Generation (RAG) architecture that combines:
- Streamlit frontend
- Firebase Authentication for sign-in/sign-up
- Ollama embeddings and chat model for retrieval and answer generation
- A local travel knowledge base stored in JSON

This project allows users to sign in with email and password, ask questions about attractions, opening hours, ticket prices, locations, and get answers grounded in the project’s travel guide instead of relying on vague general knowledge.

## Student and Project Information

- **Student name:** `Phạm Thiện Nhân`
- **Student ID:** `25127442`
- **Course / class:** `25C09`
- **Chosen city:** Ho Chi Minh City, Vietnam

Replace the bracketed fields with the student's information before submitting.

## Features

- User sign up and sign in using Firebase Email/Password authentication
- Clean and simple chat interface built with Streamlit
- Top-k document retrieval using cosine similarity
- Answer generation from Ollama based on retrieved context
- Display of source references and retrieved documents for each response
- Easy-to-extend knowledge base via `knowledge_base.json`

## Tech Stack

- Python 3.10+
- Streamlit
- Firebase REST API
- Ollama
- NumPy
- python-dotenv

## Project Structure

```text
SIGN-IN-TRAVEL-ASSISTANT-WITH-RAG-CHAT/
├── app.py                 # Main Streamlit app
├── firebase_client.py     # Firebase sign-in/sign-up logic
├── rag.py                # Embedding, retrieval, and LLM answer generation logic
├── knowledge_base.json   # Ho Chi Minh City travel knowledge base
├── .env.example          # Environment variable template
├── requirement.txt       # Python dependencies
├── README.md             # Project documentation
├── .env                  # Local environment settings (not committed)
└── .venv                 # Virtual environment (optional)
```

## Requirements

Before running the project, make sure you have:

- Python 3.10 or later
- Ollama installed and running locally
- A Firebase project with Email/Password Authentication enabled
- A public or local URL for Ollama if you need to access it remotely (for example via Pinggy, ngrok, or another tunnel)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/PTNhan-2538/SIGN-IN-TRAVEL-ASSISTANT-WITH-RAG-CHAT.git
cd SIGN-IN-TRAVEL-ASSISTANT-WITH-RAG-CHAT
```

2. Create a virtual environment and install dependencies. On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirement.txt
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
```

3. Create a local `.env` file based on `.env.example`. On Windows:

```bash
copy .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

4. Fill in the values in `.env`:

```env
# Ollama & Pinggy Server Configuration
OLLAMA_PUBLIC_URL=https://your-pinggy-url.pinggy.link

# Firebase Web / REST API Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
```

### Environment variables

- `OLLAMA_PUBLIC_URL`: The public URL used to reach the Ollama service through a tunnel. The app calls:
  - `POST {OLLAMA_PUBLIC_URL}/api/embed`
  - `POST {OLLAMA_PUBLIC_URL}/api/chat`
- `FIREBASE_API_KEY`: The API key for your Firebase project.
- `FIREBASE_AUTH_DOMAIN`: The Firebase Auth domain for your project.

## Prepare Ollama Models

Pull the required models:

```bash
ollama pull embeddinggemma
ollama pull qwen3:4b
```

If Ollama is running locally, ensure that the API is reachable from the machine running this app. If necessary, expose it through a tunnel.

## Run the Application

Make sure the Ollama service and required models are available, then run this command from the project directory:

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Test Questions and Results

The table below is a test plan for the current `knowledge_base.json`. The **retrieved IDs** and **correctness** fields are intentionally marked pending: they must be recorded from actual app runs because retrieval rankings depend on the embedding model and runtime environment. For each run, copy the IDs shown in the app's retrieved-context panel, check whether the answer matches the guide, and classify any incorrect result as a retrieval or generation failure (or missing data when the guide does not contain the answer).

| # | Question | Expected entry ID | Retrieved IDs (actual run) | Answer correct? | Failure stage / notes |
|---|---|---|---|---|---|
| 1 | What are the adult admission fee and opening hours for Independence Palace? | G02 | Pending test | Pending test | Pending test |
| 2 | What kinds of items can visitors buy at Ben Thanh Market? | G01 | Pending test | Pending test | Pending test |
| 3 | Which district is the War Remnants Museum in? | G05 | Pending test | Pending test | Pending test |
| 4 | **Paraphrase:** Where can I get a 360-degree view of Ho Chi Minh City and the Saigon River? | G07 | Pending test | Pending test | Pending test |
| 5 | Is there a ski resort in Ho Chi Minh City? | None — not in the guide | Pending test | Pending test | Pending test; expected response: “I don't know based on the provided travel guide.” |
| 6 | What is Ben Thanh Market's phone number? | None — not in the guide | Pending test | Pending test | Pending test; expected response: “I don't know based on the provided travel guide.” |

For questions 1–4, the expected entry should appear among the retrieved IDs and the answer should be supported by that entry. For questions 5–6, retrieval may still return loosely related entries; the answer is correct only if the assistant does not invent the missing information. If the expected entry is absent, mark **retrieval**; if it is present but the response is unsupported or incorrect, mark **generation**; if the guide lacks the requested fact, mark **missing data**.

## How to Use

1. Open the app in the browser.
2. Sign up or sign in using your email and password.
3. After login, ask questions like:
   - What time does Independence Palace open?
   - What does Ben Thanh Market sell?
   - Is there a skiing location here?
4. The app will:
   - retrieve the most relevant travel documents
   - compare similarity using vector embeddings
   - generate a response from Ollama using the retrieved context
   - show the source references for verification

## Important Notes

- The system answers only from `knowledge_base.json` and the retrieved context, not from general world knowledge.
- If the answer cannot be found in the available guide, the response will be:
  `I don't know based on the provided travel guide.`
- Make sure the Firebase API key is valid and Ollama is online before using the app.

## Known Limitations

- The knowledge base is a small, manually maintained guide; it may not cover every question or reflect current prices, schedules, or conditions.
- Retrieval always returns the top matching entries when the knowledge base is available. There is no relevance-score threshold, so unrelated entries may be passed to the language model.
- The model is instructed to stay within retrieved context, but generated answers can still be incomplete or incorrect. Check the cited entry and source.
- The app depends on Ollama availability and network/tunnel stability. Slow model responses or an unstable connection can cause long waits or request failures.
- Chat history is held in the current Streamlit session and is not persisted as a user account history.
- Firebase configuration, an accessible Ollama endpoint, and the required Ollama models must be supplied by the person running the app.

## AI Tools

GitHub Copilot was used to assist with code and README edits. AI-generated suggestions should be reviewed against the source code and knowledge base.

## Demonstration Video

[Watch the project demonstration](ADD_DEMONSTRATION_VIDEO_URL)

Replace `ADD_DEMONSTRATION_VIDEO_URL` with a shareable link to the demonstration video before submitting.

## Extending the Project

You can easily extend the project by:

- adding more travel entries to `knowledge_base.json`
- changing the embedding or chat model in `rag.py`
- integrating a database or persistent chat history storage
- adding filtering by category, score-based ranking, or multilingual support

## License

This project is intended for learning and internal development purposes. If you plan to use it in a commercial or public product, review the data sources and licensing terms before deployment.

## References

- Streamlit: https://streamlit.io/
- Ollama: https://ollama.com/
- Firebase Auth REST API: https://firebase.google.com/docs/reference/rest/auth
