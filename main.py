"""Main entry point for the CLI tool."""

from docucite.chains import ChainApp

CHUNK_OVERLAP = 1500
CHUNK_SIZE = 150
DB_PATH = "data/chroma"


def run() -> None:
    """Runs the app."""

    print("Setting up the session...")
    upload_documents = input(
        "Enter (n/N) for new document, any key to load existing one. "
    )

    title = None
    upload_doc = False

    if upload_documents.lower() == "n":
        upload_doc = True
        title = input("Enter title of document: ")

    chain_app = setup(title, upload_doc)
    print("Event loop started. Type 'quit' to exit.")

    while True:
        user_input = input("Enter your question: ")

        # Check for exit condition
        if user_input.lower() == "quit":
            print("Exiting...")
            break

        # Query model
        context = ""
        prompt = chain_app.build_prompt_template()
        response = chain_app.query(prompt, user_input)
        print("\n---------------------")
        print(response["result"], end="\n")
        print(response["metadata"])
        # print(f"Source: {response[-1].get("metadata")}")


def setup(title: str, load_documents=False) -> ChainApp:
    """Setup a session. Either loads document from disk, or loads an already uploaded document."""

    chain_app = ChainApp()

    if load_documents:
        chain_app.load_pdf(path=DB_PATH, document_title=title)
        chain_app.split_document(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chain_app.load_embeddings()

    return chain_app


if __name__ == "__main__":
    run()
