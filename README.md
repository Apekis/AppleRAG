

# ApplePay RAG Support

Production-grade RAG chatbot answering Apple Pay support queries using only public sources with citations.


## Instructions

In order to start the service locally, please intall the requierments.txt dependencies.
Add your OPENAI_API_KEY key as an env. variable.
Then start the frontend with npm run dev --prefix frontend from the top ("RAG") directory.
Then start the backend with uvicorn app:app --host 0.0.0.0 --port 8000 --reload from the backend ("RAG\backend") directory.


## Usage

After that, the service should appear when opening a browser at http://localhost:5173/.
There you have a window where you can ask questions regarding ApplePay.
After asking the question, the answer as well as some citations and the top chunks should appear.