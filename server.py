from papercast.pipelines import Pipeline
from papercast.collectors import ArxivCollector
from papercast.processors import SayProcessor
from papercast.processors import GROBIDProcessor
from papercast.publishers import GithubPagesPodcastPublisher
from papercast.server import Server
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("PAPERCAST_ZOTERO_API_KEY", None)
user_id = os.getenv("PAPERCAST_ZOTERO_USER_ID", None)

if api_key is None or user_id is None:
    raise ValueError("Zotero API key or user ID not found")

pipeline = Pipeline(name="default")

pipeline.add_processor(
    "arxiv", ArxivCollector(pdf_dir="data/pdfs", json_dir="data/json")
)

pipeline.add_processor(
    "grobid",
    GROBIDProcessor(
        remove_non_printable_chars=True, grobid_url="http://localhost:8070/"
    ),
)

pipeline.add_processor("say", SayProcessor(mp3_dir="data/mp3s", txt_dir="data/txts"))

pipeline.add_processor(
    "github_pages",
    GithubPagesPodcastPublisher(
        title="example-papercast",
        base_url="https://example.github.io/papercast/",
        language="en-us",
        subtitle="Drinking the firehose one paper at a time",
        copyright="Rights to paper content are reserved by the authors for each paper. I make no claim to ownership or copyright of the content of this podcast.",
        author="Anonymous Author",
        email="email@example.com",
        description="A podcast of research articles, created with papercast (github.com/papercast-dev/papercast)",
        cover_path="https://example.github.io/papercast/cover.jpg",
        categories=["Mathematics", "Tech News", "Courses"],
        keywords=[
            "Machine Learning",
            "Natural Language Processing",
            "Artificial Intelligence",
        ],
        xml_path="/path/to/your/papercast/feed.xml",
    ),
)

pipeline.connect("arxiv", "pdf", "grobid", "pdf")
pipeline.connect("grobid", "text", "say", "text")
pipeline.connect("say", "mp3_path", "github_pages", "mp3_path")
pipeline.connect("grobid", "abstract", "github_pages", "description")
pipeline.connect("grobid", "title", "github_pages", "title")

server = Server(pipelines={"default": pipeline})

if __name__ == "__main__":
    server.run()