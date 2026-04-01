import numpy as np
from pathlib import Path
import pytest
import json
from src.categories import get_categories_ids, add_category

def test_get_categories_ids(db_session):

    all_cateogries = get_categories_ids(category_names=None, conn=db_session)

    assert isinstance(all_cateogries, dict)
    assert len(all_cateogries) > 0
    for name, id in all_cateogries.items():
        assert isinstance(name, str)
        assert isinstance(id, int)
    
    first_two_categories = list(all_cateogries.keys())[:2]

    filtered_categories = get_categories_ids(category_names=first_two_categories, conn=db_session)
    assert isinstance(filtered_categories, dict)
    assert len(filtered_categories) == 2
    for name in first_two_categories:
        assert name in filtered_categories

def test_add_category(db_session):
    new_category_name = "Test Category"
    response = add_category(category_name=new_category_name, conn=db_session)

    assert response.status == "ok"
    assert response.id_ is not None
    assert response.exists == False

    # Try adding the same category again to test duplicate handling
    duplicate_response = add_category(category_name=new_category_name, conn=db_session)

    assert duplicate_response.status == "ok"
    assert duplicate_response.id_ == response.id_
    assert duplicate_response.exists == True