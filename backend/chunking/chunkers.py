#chunkers
#fixed size chunker----------------------------------------------
def fixed_chunk_text(text:str, chunk_size:int=512, overlap:int=0):
    words = text.split()
    chunks=[]; i=0
    while i < len(words):
        chunks.append(" ".join(words[i:i+chunk_size]))
        i += max(1, chunk_size-overlap)
    return chunks

#semantic chunker------------------------------------------------------------------
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab')

semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_chunk_text(text, similarity_threshold=0.8, max_tokens=500):
    """
    Splits text into semantic chunks based on sentence similarity and max token length.
    """
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return []
    embeddings = semantic_model.encode(sentences)
    chunks = []
    current_chunk = [sentences[0]]
    current_embedding = embeddings[0]
    for i in range(1, len(sentences)):
        sim = cosine_similarity([current_embedding], [embeddings[i]])[0][0]
        chunk_token_count = len(" ".join(current_chunk)) // 4
        if sim >= similarity_threshold and chunk_token_count < max_tokens:
            current_chunk.append(sentences[i])
            current_embedding = (current_embedding + embeddings[i]) / 2
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]
            current_embedding = embeddings[i]
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

#recursive chunker------------------------------------------------------------------

def recursive_chunk_text(text, max_chunk_size=1000):
    """
    Recursively splits a block of text into chunks that fit within size constraints.
    Tries splitting by sections, then newlines, then sentences.
    """
    import nltk
    nltk.download("punkt", quiet=True)

    def split_chunk(chunk):
        if len(chunk) <= max_chunk_size:
            return [chunk]
        # Try splitting by double newlines
        sections = chunk.split("\n\n")
        if len(sections) > 1:
            result = []
            for section in sections:
                if section.strip():
                    result.extend(split_chunk(section.strip()))
            return result
        # Try splitting by single newline
        sections = chunk.split("\n")
        if len(sections) > 1:
            result = []
            for section in sections:
                if section.strip():
                    result.extend(split_chunk(section.strip()))
            return result
        # Fallback: split by sentences
        sentences = nltk.sent_tokenize(chunk)
        chunks, current_chunk, current_size = [], [], 0
        for sentence in sentences:
            if current_size + len(sentence) > max_chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_size = len(sentence)
            else:
                current_chunk.append(sentence)
                current_size += len(sentence)
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    return split_chunk(text)

#structure based chunker------------------------------------------------------------------

def structure_chunk_text(text):
    """
    Splits text into chunks based on detected headings (e.g., CHAPTER, section numbers).
    """
    lines = text.split("\n")
    chunks = []
    current_chunk = []

    heading_tags = ('\h1','\h2','\h3','\h4','\h5','\h6')
    for line in lines:
        if any(heading in (line.strip()) for heading in heading_tags) and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
        else:
            current_chunk.append(line)
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return chunks

#LLM based chunker------------------------------------------------------------------
from openai import OpenAI
import os
os.environ["OPENAI_API_KEY"]="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"


def llm_chunk_text(text, chunk_size=1000, model="gpt-4o-mini", api_key=None):
    """
    Uses an LLM to find semantically coherent chunk boundaries around a target chunk size.
    """
    client = OpenAI(api_key=api_key)
    def get_chunk_boundary(text_segment):
        prompt = f"""
        Analyze the following text and identify the best point to split it
        into two semantically coherent parts. The split should occur near {chunk_size} characters.
        Text:
        \"\"\"{text_segment}\"\"\"
        Return only the integer index (character position) within this text where the split should occur.
        """
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a text analysis expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        split_str = response.choices[0].message.content.strip()
        try:
            split_point = int(split_str)
        except ValueError:
            split_point = chunk_size
        return split_point

    chunks = []
    remaining_text = text
    while len(remaining_text) > chunk_size:
        text_window = remaining_text[:chunk_size * 2]
        split_point = get_chunk_boundary(text_window)
        if split_point < 100 or split_point > len(text_window) - 100:
            split_point = chunk_size
        chunks.append(remaining_text[:split_point].strip())
        remaining_text = remaining_text[split_point:].strip()
    if remaining_text:
        chunks.append(remaining_text)
    return chunks

