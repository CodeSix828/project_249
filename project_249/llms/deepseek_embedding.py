import openai
from ..config.settings import settings


class DeepseekEmbedding:
    def __init__(self):
        self.embedding_model = openai.OpenAI(
            api_key=settings.EMBEDDING_EFFECTIVE_KEY,
            base_url=settings.EMBEDDING_EFFECTIVE_URL,
        )
        self.model_name = settings.EMBEDDING_MODEL_NAME

    def get_embedding(self, content: str = ""):
        response = self.embedding_model.embeddings.create(
            model=self.model_name,
            input=content,
        )
        return response.data[0].embedding
