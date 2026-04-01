import requests


def get_paper_info(doi):
    # OpenAlex expects the full doi.org URL as the identifier
    clean_doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    full_doi_url = f"https://doi.org/{clean_doi}"
        
    url = f"https://api.openalex.org/works/{full_doi_url}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # 1. Reconstruct the abstract from the inverted index
        abstract_text = "No abstract available."
        inverted_index = data.get("abstract_inverted_index")
        
        if inverted_index:
            # Find the highest index to know how many words are in the abstract
            max_pos = max([pos for positions in inverted_index.values() for pos in positions])
            words = [""] * (max_pos + 1)
            
            # Place each word in its correct position in the list
            for word, positions in inverted_index.items():
                for pos in positions:
                    words[pos] = word
                    
            abstract_text = " ".join(words)
            
        # 2. Extract authors safely
        authors = [a["author"]["display_name"] for a in data.get("authorships", [])]
        
        # 3. Extract journal/venue name safely
        primary_loc = data.get("primary_location") or {}
        source = primary_loc.get("source") or {}
        venue = source.get("display_name", "Unknown Venue")

        print(data) 
        return {
            "title": data.get("title"),
            "abstract": abstract_text,
            "authors": authors,
            "year": data.get("publication_year"),
            "venue": venue
        }
    else:
        return {"error": f"API Error {response.status_code}: Paper not found"}

# Test with your arXiv DOI!
my_doi = "http://dx.doi.org/10.1145/2939672.2939785"
paper_data = get_paper_info(my_doi)

if "error" in paper_data:
    print(paper_data["error"])
else:
    print(f"Title: {paper_data.get('title')}")
    print(f"Authors: {', '.join(paper_data.get('authors', []))}")
    print(f"Year: {paper_data.get('year')}")
    print(f"Venue: {paper_data.get('venue')}\n")
    print(f"Abstract: {paper_data.get('abstract')}")