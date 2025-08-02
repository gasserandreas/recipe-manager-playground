Overall goal: Built a recipe web-scraper which loads the recipe context html text for a given url and provide the context as meaningful markdown file usable for LLM.

requirement 1: download web page context for given url
requirement 2: convert recipe context to markdown, ignore everything else
requirement 3: markdown data should follow a specific template usable by LLMs later on
requirement 4: use following libraries: markdownify, AsyncHtmlLoader from langchain_community.document_loaders 