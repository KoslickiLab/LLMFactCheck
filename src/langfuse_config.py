from decouple import config
from langfuse import Langfuse

#Description: 
#The code snippet initializes the Langfuse client.

langfuse = Langfuse(
    public_key=config("LANGFUSE_PUBLIC_KEY"),
    secret_key=config("LANGFUSE_SECRET_KEY"),
    host=config("LANGFUSE_HOST"),
)

__all__ = ["langfuse"]
