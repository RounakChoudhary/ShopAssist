from rag.embedding import  get_embedding

embedding  =  get_embedding("What is the return policy?")
print(type(embedding))
print(embedding.shape)
print(embedding[:5])