import os
import json
import requests



def search_pokemon_items(query="charizard", limit=5, token="", sort="endingSoonest", filter_str=""):
    if not token:
        with open(os.path.join(os.path.dirname(__file__), "mock_response.json")) as f:
            return json.load(f)

    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "q": query,
        "limit": limit,
        "sort": sort,
    }

    if filter_str:
        params["filter"] = filter_str

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
