import os
import google.generativeai as genai

def get_recommendations(user_interest, trip_interests):
    """
    Uses the Gemini API to get trip recommendations based on user interest.
    
    Args:
        user_interest (str): The interest provided by the user.
        trip_interests (list): A list of interests from all trips.
        
    Returns:
        list: A list of recommended trip interests.
    """
    # Configure the Gemini API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"Given a user's interest '{user_interest}', which of the following trip interests are most relevant? Please return a comma-separated list of the relevant interests. Trip interests: {', '.join(trip_interests)}"
    
    response = model.generate_content(prompt)
    
    try:
        recommended_trips = response.text.strip().split(',')
        print("recommentd",recommended_trips)
    except Exception as e:
        print(f"Error processing Gemini response: {e}")
        recommended_trips = []

    return [trip.strip() for trip in recommended_trips]
