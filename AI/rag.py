import os
import math
import tiktoken
from typing import List, Dict, Any
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
PINECONE_APIKEY = os.environ['PINECONE_APIKEY']
INDEX_NAME = os.environ["INDEX_NAME"]
EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_APIKEY)
index = pc.Index(INDEX_NAME)

def generar_embedding_consulta(consulta: str) -> List[float]:
    """
    Genera el embedding para una consulta.
    
    Args:
        consulta (str): Texto de la consulta
    
    Returns:
        List[float]: Embedding de la consulta
    """
    response = client.embeddings.create(
        input=consulta,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def buscar_en_pinecone(consulta: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Realiza una búsqueda de similitud en los embeddings.
    
    Args:
        consulta (str): Texto de la consulta
        top_k (int): Número de resultados a devolver
    
    Returns:
        List[Dict[str, Any]]: Resultados de la búsqueda
    """
    # Conectar al índice
    index = pc.Index(INDEX_NAME)
    
    # Generar embedding de la consulta
    query_embedding = generar_embedding_consulta(consulta)
    
    # Realizar búsqueda
    resultados = index.query(
        vector=query_embedding, 
        top_k=top_k, 
        include_metadata=True
    )
    
    return resultados['matches']

def chunk_text(text: str, max_tokens: int = 500, overlap: int = 100) -> List[str]:
    """
    Divide el texto en chunks de tokens con un overlap para mantener contexto.
    
    Args:
        text (str): Texto a dividir
        max_tokens (int): Número máximo de tokens por chunk
        overlap (int): Número de tokens de superposición entre chunks
    
    Returns:
        List[str]: Lista de chunks de texto
    """
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    chunks = []
    
    for i in range(0, len(tokens), max_tokens - overlap):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk = tokenizer.decode(chunk_tokens)
        chunks.append(chunk)
    
    return chunks

def cargar_chunk(metadata: Dict[str, Any]) -> str:
    """
    Carga el chunk de texto original basado en los metadatos.
    """
    nombre_archivo = metadata['documento_original']
    ruta_completa = os.path.join('docs', nombre_archivo)
    
    try:
        with open(ruta_completa, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            
            # Dividir en chunks usando la función chunk_text
            chunks = chunk_text(contenido)
            
            # Convertir chunk_numero a entero, redondeando 
            chunk_numero = int(math.floor(metadata['chunk_numero']))
            
            # Devolver el chunk si existe, sino string vacío
            return chunks[chunk_numero] if chunk_numero < len(chunks) else ""
    
    except Exception as e:
        print(f"Error cargando chunk: {e}")
        return ""
    
def preparar_contexto(resultados: List[Dict[str, Any]]) -> str:
    """
    Prepara un contexto concatenando los chunks más relevantes.
    """
    contexto = "Contexto relevante:\n"
    for resultado in resultados:
        chunk = cargar_chunk(resultado['metadata'])
        contexto += f"--- De {resultado['metadata']['documento_original']} ---\n"
        contexto += chunk + "\n\n"
    return contexto


def get_rag_context(query:str):
    results = buscar_en_pinecone(query)
    contexto = preparar_contexto(results)
    return contexto


# print(get_rag_context("ubicaciones"))