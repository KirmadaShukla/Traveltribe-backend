import os
import google.generativeai as genai

def get_recommendations(user_interest, trip_interests):
    """
    Uses the Gemini API to get trip recommendations based on user interest.
    
    Args:
        user_interest (str): The interest provided by the user.
        trip_interests (list of str): A list of comma-separated interest strings from all trips.
        
    Returns:
        list: A list of recommended trip interests.
    """
    if not trip_interests:
        return []

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Create a unique, flat list of interests for the prompt
    all_individual_interests = set()
    for interest_group in trip_interests:
        all_individual_interests.update([i.strip() for i in interest_group.split(',') if i.strip()])
    
    if not all_individual_interests:
        return []

    prompt = (f"From the following list of trip interests, select the ones that are most relevant to a user with an interest in '{user_interest}'. "
              f"Return only a comma-separated list of the relevant interests. Do not add any extra text or explanation. "
              f"Trip interests: {', '.join(sorted(list(all_individual_interests)))}")
    
    try:
        response = model.generate_content(prompt)
        
        # Basic validation to check if the response is just a re-prompt or an error message
        if "interests" in response.text.lower() and len(response.text) > 100:
            print("response",response)
            return []
            
        recommended_interests = [interest.strip() for interest in response.text.strip().split(',') if interest.strip()]
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        recommended_interests = []

    return recommended_interests
