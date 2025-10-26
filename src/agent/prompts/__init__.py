from pathlib import Path

_prompt_folder = Path(__file__).parent

with _prompt_folder.joinpath("author_info.txt").open("r", encoding="utf-8") as f:
    AUTHOR_INFO_PROMPT = f.read()

with _prompt_folder.joinpath("book_description.txt").open("r", encoding="utf-8") as f:
    BOOK_SUMMARY_PROMPT = f.read()

__all__ = ["AUTHOR_INFO_PROMPT", "BOOK_SUMMARY_PROMPT"]