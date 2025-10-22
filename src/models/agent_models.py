from typing import Literal, Optional

from pydantic import BaseModel, Field


class AuthorInfo(BaseModel):
    """
    Represents information about an author.

    Attributes
    ----------
    name : Optional[str]
        The name of the author.
    birth_date : Optional[str]
        The birth date of the author in the format YYYY-MM-DD.
    death_date : Optional[str]
        The death date of the author, if applicable, in the format YYYY-MM-DD.
    nationality : Optional[str]
        The nationality of the author.
    sex : Optional[Literal["M", "F"]]
        The sex of the author, either "M" for male or "F" for female.
    """

    name: Optional[str] = Field(None, description="Name of the author")
    birth_date: Optional[str] = Field(
        None, description="Birth date of the author YYYY-MM-DD"
    )
    death_date: Optional[str] = Field(
        None, description="Death date of the author, if applicable YYYY-MM-DD"
    )
    nationality: Optional[str] = Field(None, description="Nationality of the author")
    sex: Optional[Literal["M", "F"]] = Field(None, description="Sex of the author")
