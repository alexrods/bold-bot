from AI.rag import get_rag_context
from AI.get_responses import openAI_response


def info_agent(question:str) -> str:
    """
    Function to get a response from a BOLD informative agent.

    The agent is given a prompt with some context and a question from a user.
    The agent should respond with a concise answer to the question.

    Parameters
    ----------
    question : str
        The question asked by the user.

    Returns
    -------
    str
        The response of the agent to the question.
    """
    sys_prompt = f"""
        Eres un agente de BOLD una clínica especializada en restauración capilar,  
        tu tarea es responder de manera consisa las consultas del cliente.

        
        No respondas a preguntas fuera del contexto de la empresa.  
        
        Usa el siguiente contexto para responder:

        [CONTEXT]
        {get_rag_context(question)}

        Las clinicas de Bold se encuentran en: San Pedro Garza García, Chihuahua y Tampico. 
        [CONTEXT/]    
        """
    
    agent_response = openAI_response(sys_prompt, question)
    print(f"INFO_AGENT RESPONSE: {agent_response}")
    return agent_response