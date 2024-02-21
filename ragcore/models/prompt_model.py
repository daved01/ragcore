class PromptGenerator:
    """Class to manage prompt templates and to generate prompts.

    A prompt is generated from a template and two inputs. One input is the `question`, for example
    a question about some content in a document. The second input is a context string, which is a
    concatenated string of context which should be used in the prompt.

    """

    def get_prompt(self, question: str, context_str: str) -> str:
        """Creates a prompt from the template, the question, and the context.

        Typically, the question is the user input and the context is retrieved from a database.

        Args:
            question: A question as a string.

            context_str: A string with all context which should be part of the prompt.

        Returns:
            A prompt as a string to be used for a LLM.

        """

        return f"""Use the following pieces of context, provided in the triple backticks,
        to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        If you have the information available from the metadata of the context under the field "page",
        cite your answers with page numbers in square brackets after each sentence or paragraph.
        Context: ```{context_str}```
        Question: ```{question}```
        Helpful Answer:"""
