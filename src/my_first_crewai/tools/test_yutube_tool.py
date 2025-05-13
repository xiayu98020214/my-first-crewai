from crewai_tools import YoutubeVideoSearchTool

youtube_search_tool = YoutubeVideoSearchTool(
    config=dict(
        llm=dict(
            provider="deepseek", # or google, openai, anthropic, llama2, ...
            config=dict(
                model="deepseek-chat",
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="google", # or openai, ollama, ...
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )
)

