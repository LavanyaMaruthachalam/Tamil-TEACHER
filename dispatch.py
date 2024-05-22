import json
import openai
import re
import googletrans

# Load the kural data
# Load the Thirukkural data from a JSON file
file_path = r"C:\Users\Lavanya\Downloads\thirukural_git.json"  # Adjust the path accordingly
with open(file_path, 'r', encoding='utf-8') as file:
    kural_data = json.load(file) 





api_key = "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"
openai.api_key = api_key





#RULE BASED FUNCTION







# Define the function to get responses based on Thirukkural


def get_thirukkural_response(kural_data, query_type, query_value, translate_to=None, author_alias=None, detail=None):
    """Retrieve a Thirukkural response based on query type, value, and optional author explanation."""
    translator = googletrans.Translator()
    responses = []
    author_map = {
        'mu_va': 'ta_mu_va',
        'mu va': 'ta_mu_va',
        'ta_mu_va': 'ta_mu_va',
        'salamon': 'ta_salamon',
        'ta_salamon': 'ta_salamon',
        'சாலமன் பாப்பையா': 'ta_salamon'
    }


    # Helper function to perform translation
    def translate(text, target_lang):
        """Translate text using Google Translate."""
        if target_lang:
            try:
                return translator.translate(text, src='ta' if target_lang == 'en' else 'en', dest=target_lang).text
            except Exception as e:
                print(f"Translation failed: {e}")
                return text
        return text

    


        # Identify kurals based on query_type
    kurals_to_process = []
    if query_type == 'section_name':
        kurals_to_process = [k for k in kural_data['kurals'] if k['section'] == query_value]
    elif query_type == 'chapter_name':
        kurals_to_process = [k for k in kural_data['kurals'] if k['chapter'] == query_value]
    elif query_type in ['keyword', 'starts_with', 'ends_with']:
        for kural in kural_data['kurals']:
            if (query_type == 'keyword' and query_value in ' '.join(kural['kural']).lower()) or \
               (query_type == 'starts_with' and kural['kural'][0].startswith(query_value)) or \
               (query_type == 'ends_with' and kural['kural'][-1].endswith(query_value)):
                kurals_to_process.append(kural)

    # Generate responses for each kural
    for kural in kurals_to_process:
        kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
        if translate_to == 'ta':
            english_meaning = kural['meaning'].get('en', "No English translation available.")
            translated_text = translate(english_meaning, 'en', 'ta')
            responses.append(f"{kural_text}\nMeaning (Tamil): {translated_text}")
        elif author_alias and author_alias in author_map:
            author_key = author_map[author_alias]
            explanation = kural['meaning'].get(author_key, "No explanation available.")
            if translate_to == 'en':
                translated_text = translate(explanation, 'ta', 'en')
                responses.append(f"{kural_text}\nExplanation by {author_alias} (English): {translated_text}")
            else:
                responses.append(f"{kural_text}\nExplanation by {author_alias}: {explanation}")
        else:
            english_meaning = kural['meaning'].get('en', "No English translation available.")
            responses.append(f"{kural_text}\nMeaning (English): {english_meaning}")

            

    # Define a function to format the response for kurals
    def format_kural_response(kural):
        """Format the response for a single kural with optional translation or explanation."""
        kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
        if author_alias and author_alias in author_map:
            author_key = author_map[author_alias]
            explanation = kural['meaning'].get(author_key, "No explanation available.")
            if translate_to:
                explanation = translate(explanation, translate_to)
            response = f"{kural_text}\nExplanation by {author_key.replace('ta_', '')}: {explanation}"
        elif translate_to:
            english_meaning = kural['meaning'].get('en', "No English translation available.")
            translated_meaning = translate(english_meaning, translate_to)
            response = f"{kural_text}\nMeaning ({translate_to.capitalize()}): {translated_meaning}"
        else:
            english_meaning = kural['meaning'].get('en', "No English translation available.")
            response = f"{kural_text}\nMeaning (English): {english_meaning}"
        return response


        # Rule 1 & 2: Section and/or Chapter based queries
    if query_type in ['section_name', 'chapter_name']:
        for kural in kural_data['kurals']:
            if (query_type == 'section_name' and kural['section'] == query_value) or \
               (query_type == 'chapter_name' and kural['chapter'] == query_value):
                kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
                if author_alias and author_alias in author_map:
                    author_key = author_map[author_alias]
                    explanation = kural['meaning'].get(author_key, "No explanation available.")
                    kural_text += f"\nExplanation by {author_key}: {explanation}"
                else:
                    kural_text += f"\nMeaning (English): {kural['meaning']['en']}"
                responses.append(kural_text)

    # Rule 3, 9: Keyword based English meanings
    if query_type == 'keyword':
        kurals_by_keyword = [kural for kural in kural_data['kurals'] if query_value in ' '.join(kural['kural']).lower()]
        if detail == 'english_meaning':
            responses.extend([f"Kural {k['number']}: {' '.join(k['kural'])}\nMeaning (English): {k['meaning']['en']}" for k in kurals_by_keyword])
        elif detail == 'chapter_list':
            chapters = set(k['chapter'] for k in kurals_by_keyword)
            responses.extend(list(chapters))
        else:
            for kural in kurals_by_keyword:
                if author_alias in author_map:
                    kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
                    author_key = author_map[author_alias]
                    explanation = kural['meaning'].get(author_key, "No explanation available.")
                    responses.append(f"{kural_text}\nExplanation by {author_key}: {explanation}")

    # Rule 7, 8, 13, 14: Kurals starting/ending with a specific word
    if query_type == 'starts_with':
        responses.extend([f"Kural {k['number']}: {' '.join(k['kural'])}" for k in kural_data['kurals'] if k['kural'][0].startswith(query_value)])
    if query_type == 'ends_with':
        responses.extend([f"Kural {k['number']}: {' '.join(k['kural'])}" for k in kural_data['kurals'] if k['kural'][-1].endswith(query_value)])





    # Fetch by kural number
    if query_type == 'kural_number':
        kural_match = next((k for k in kural_data['kurals'] if k['number'] == int(query_value)), None)
        if kural_match:
            kural_text = f"Kural {kural_match['number']}: {' '.join(kural_match['kural'])}"
            if author_alias and author_alias in author_map:
                author_key = author_map[author_alias]
                author_explanation = kural_match['meaning'].get(author_key, "No explanation available for this author.")
                responses.append(f"{kural_text}\nExplanation by {author_key.replace('ta_', '')}: {author_explanation}")
            else:
                english_meaning = kural_match['meaning'].get('en', "No English translation available.")
                responses.append(f"{kural_text}\nMeaning (English): {english_meaning}")

    # Fetch by chapter name
    elif query_type == 'chapter_name':
        kurals_in_chapter = [k for k in kural_data['kurals'] if k['chapter'].lower() == query_value.lower()]
        for kural in kurals_in_chapter:
            kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
            if author_alias and author_alias in author_map:
                author_key = author_map[author_alias]
                explanation = kural['meaning'].get(author_key, "No explanation available.")
                responses.append(f"{kural_text}\nExplanation by {author_key.replace('ta_', '')}: {explanation}")
            else:
                english_meaning = kural['meaning'].get('en', "No English translation available.")
                responses.append(f"{kural_text}\nMeaning (English): {english_meaning}")

    # Fetch by section name
    elif query_type == 'section_name':
        chapters_in_section = set(k['chapter'] for k in kural_data['kurals'] if k['section'].lower() == query_value.lower())
        for chapter in chapters_in_section:
            kurals_in_chapter = [k for k in kural_data['kurals'] if k['chapter'].lower() == chapter.lower()]
            chapter_responses = []
            for kural in kurals_in_chapter:
                kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
                english_meaning = kural['meaning'].get('en', "No English translation available.")
                chapter_responses.append(f"{kural_text}\nMeaning (English): {english_meaning}")
            responses.append(f"Chapter: {chapter}\n" + "\n".join(chapter_responses))


                # Fetch by keyword in kural, which checks for keywords in the text of the kural
    elif query_type == 'keyword':
        kurals_by_keyword = [kural for kural in kural_data['kurals'] if query_value in " ".join(kural['kural']).lower()]
        for kural in kurals_by_keyword:
            kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
            if author_alias and author_alias in author_map:
                author_key = author_map[author_alias]
                explanation = kural['meaning'].get(author_key, "No explanation available.")
                responses.append(f"{kural_text}\nExplanation by {author_key.replace('ta_', '')}: {explanation}")
            else:
                english_meaning = kural['meaning'].get('en', "No English translation available.")
                responses.append(f"{kural_text}\nMeaning (English): {english_meaning}")


# Logic to handle different types of queries
    elif query_type == 'keyword':
        if detail == 'starts_with':
            kurals_filtered = [kural for kural in kural_data['kurals'] if kural['kural'][0].startswith(query_value)]
        elif detail == 'ends_with':
            kurals_filtered = [kural for kural in kural_data['kurals'] if kural['kural'][-1].endswith(query_value)]
        for kural in kurals_filtered:
            kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
            responses.append(kural_text)

    elif query_type == 'author_translation':
        kurals_filtered = [kural for kural in kural_data['kurals'] if author_alias in kural['meaning']]
        for kural in kurals_filtered:
            explanation = kural['meaning'][author_alias]
            kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}\nExplanation by {author_alias}: {explanation}"
            responses.append(kural_text)

    elif query_type == 'chapter_count':
        count = sum(1 for kural in kural_data['kurals'] if kural['chapter'] == query_value)
        responses.append(f"Total kurals in chapter '{query_value}': {count}")

    # Check for the correct handling of the 'author_translation' query type
    elif query_type == 'author_translation':
        # Assuming query_value should be something like 'ta_mu_va'
        kurals_filtered = [kural for kural in kural_data['kurals'] if query_value in kural['meaning']]
        for kural in kurals_filtered:
            explanation = kural['meaning'].get(query_value)
            if explanation:  # Ensure there's a translation available
                kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}\nExplanation by {query_value}: {explanation}"
                responses.append(kural_text)



    # Fetch kurals that start or end with a specific word
    elif query_type == 'starts_with' or query_type == 'ends_with':
        kurals_filtered = [
            kural for kural in kural_data['kurals']
            if (query_type == 'starts_with' and kural['kural'][0].startswith(query_value)) or
               (query_type == 'ends_with' and kural['kural'][1].endswith(query_value))
        ]
        for kural in kurals_filtered:
            kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
            english_meaning = kural['meaning'].get('en', "No English translation available.")
            responses.append(f"{kural_text}\nMeaning (English): {english_meaning}")

            # Fetch kurals containing a keyword with different requirements
    elif query_type == 'keyword':
        filtered_kurals = [kural for kural in kural_data['kurals'] if query_value in " ".join(kural['kural']).lower()]
        if detail == 'chapter_list':
            # List chapters that contain the keyword
            chapter_set = set(kural['chapter'] for kural in filtered_kurals)
            responses = list(chapter_set)
        elif detail in ['mu_va', 'ta_salamon']:
            # Show kural and explanation by the specific author for the keyword
            for kural in filtered_kurals:
                kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
                author_explanation = kural['meaning'].get(detail, "No explanation available.")
                responses.append(f"{kural_text}\nExplanation by {detail}: {author_explanation}")
        elif detail == 'starts_with':
            # Kurals that start with the specific word
            responses = [f"Kural {k['number']}: {' '.join(k['kural'])}" for k in filtered_kurals if k['kural'][0].startswith(query_value)]
        elif detail == 'ends_with':
            # Kurals that end with the specific word
            responses = [f"Kural {k['number']}: {' '.join(k['kural'])}" for k in filtered_kurals if k['kural'][1].endswith(query_value)]
        else:
            # Default to showing English translation only
            for kural in filtered_kurals:
                kural_text = f"Kural {kural['number']}: {' '.join(kural['kural'])}"
                english_meaning = kural['meaning'].get('en', "No English translation available.")
                responses.append(f"{kural_text}\nMeaning (English): {english_meaning}")




    return "\n".join(responses) if responses else "No Kural found matching the query."




#  AI-based




# Function to handle AI-based interactions using GPT-4
def handle_ai_based(query):
    try:
        # Setup for the chat completion call
        response = openai.ChatCompletion.create(
            model="gpt-4o-2024-05-13",  # Specify the correct model identifier if different
            messages=[
                {"role": "system", "content": "You are a chatbot trained to answer questions about Thirukkural.Thirukural has 1330 kurals or verses.If questions are above 1330 kurals you have to explain there is no kurals there more than 1330.You are an AI trained extensively on the Thirukkural, capable of understanding and responding in Tamil, English, and Tanglish.You have detailed knowledge of the commentaries by Mu. Varadarasanar and Salamon Pappaiya on the Thirukkural verses.You can provide explanations, interpret meanings, and relate verses to modern contexts as per the commentators' insights.You are also a chatbot trained to answer questions about Athichudi.You are a dedicated chatbot for Thirukkural and athichudi alone,if user queries apart from this just say sorry and say you can only answer for Thirukkural and Athichudi"},
                {"role": "user", "content": query}
            ],
            temperature=0.7,  # Adjust temperature if needed for creativity
            max_tokens=300  # Adjust max tokens based on the length of response needed
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"An error occurred: {str(e)}"
    





def dispatcher(query, kural_data):
    details = extract_query_details(query)
    
    if details['query_type'] == 'kural_number' and 'kural_number' in details:
        return get_thirukkural_response(kural_data, 'kural_number', details['kural_number'])
    elif details['query_type'] == 'chapter_name' and 'chapter_name' in details:
        return get_thirukkural_response(kural_data, 'chapter_name', details['chapter_name'])
    else:
        return handle_ai_based(query)


# Example of how to set up the query details extraction (placeholder function)


def extract_query_details(query):
    """
    Extracts details from the user's query. Attempts to determine the type of query
    and extract relevant parameters such as the kural number, or handles general conversation.
    """
    query = query.lower().strip()
    
    # Handling greetings or general inquiries
    greetings = ['hi', 'hello', 'hey']
    if any(greeting in query.split() for greeting in greetings):
        return {'query_type': 'greeting'}
    
    # Handling queries about Thirukkural specific details
    kural_number_match = re.search(r"\bkural number (\d+)\b", query)
    if kural_number_match:
        return {'query_type': 'kural_number', 'kural_number': int(kural_number_match.group(1))}

    chapter_name_match = re.search(r"chapter name ([\w\s]+)", query)
    if chapter_name_match:
        return {'query_type': 'chapter_name', 'chapter_name': chapter_name_match.group(1).strip()}

    # Check for general inquiries about Thirukkural
    if 'thirukkural' in query:
        return {'query_type': 'info_about_thirukkural'}

    # Default to treating the query as free text if no patterns match
    return {'query_type': 'free_text', 'query': query}


# Assuming the rest of your functions and loading mechanisms are defined as in your previous examples


# Load Thirukkural data
#kural_data = load_kural_data("/content/drive/MyDrive/THIRUKURAL/thirukural_git.json")

# Test the dispatcher
query = "What is the meaning of Kural number 555 in English?"
response = dispatcher(query, kural_data)
print(response)

query = "Kural says about leadeship"
response = dispatcher(query, kural_data)
print(response)





















