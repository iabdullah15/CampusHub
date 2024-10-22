import time
from openai import OpenAI
from googleapiclient import discovery
import json

# Translate text
def ask_assistant(query: str):

    ASSISTANT_ID = "asst_ujKwICKSjUFQ359drqh82L1F"

    # Make sure your API key is set as an environment variable.
    client = OpenAI(api_key="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")

    # Create a thread with a message.
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                # Update this with the query you want to use.
                "content": query,
            }
        ]
    )

    # Submit the thread to the assistant (as a new run).
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=ASSISTANT_ID
    )
    print(f"👉 Run Created: {run.id}")

    # Wait for run to complete.
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(f"🏃 Run Status: {run.status}")
        time.sleep(1)
    else:
        print(f"🏁 Run Completed!")

    # Get the latest message from the thread.
    message_response = client.beta.threads.messages.list(thread_id=thread.id)
    messages = message_response.data

    # Print the latest message.
    latest_message = messages[0]
    print(f"💬 Response: {latest_message.content[0].text.value}")
    
    
    



def perspective(post_content:str):
    
    API_KEY = "AIzaSyBqueBXYTNwxUxHiJEyie962Gg7c2QxGEo"
    
    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )

    analyze_request = {
        "comment": {"text": post_content},
        "requestedAttributes": {"TOXICITY": {}, "PROFANITY": {}, "IDENTITY_ATTACK": {}, "INSULT": {}, "THREAT":{}},
    }

    response = client.comments().analyze(body=analyze_request).execute()
    json_response = json.dumps(response, indent=2)
    response_dict = json.loads(json_response)

    attr_scores = response_dict.get('attributeScores')
    attrs_list = []
    scores_list = []

    scores_dict = dict()

    # Get all attributes and append them to a list
    for i in attr_scores:
        attrs_list.append(i)

    for i in range(len(attr_scores)):
        
        score =  attr_scores[attrs_list[i]]['summaryScore']['value']
        
        scores_dict.update({attrs_list[i]: score})
    
        
    return scores_dict
    
    
    
    
def determine_moderation_action(attribute_scores):
    actions = {}
    final_action = 'Accept'  # Default action

    for attribute, score in attribute_scores.items():
        if attribute in ['TOXICITY', 'INSULT', 'PROFANITY']:
            # High Priority Attributes
            if score < 0.45:
                actions[attribute] = 'Accept'
            elif 0.45 <= score <= 0.6:
                actions[attribute] = 'Issue Warning'
                final_action = 'Issue Warning' if final_action != 'Reject' else final_action
            else:  # score > 0.6
                actions[attribute] = 'Reject'
                final_action = 'Reject'
        elif attribute == 'THREAT':
            # Moderate Priority Attribute
            if score < 0.5:
                actions[attribute] = 'Accept'
            elif 0.5 <= score <= 0.7:
                actions[attribute] = 'Issue Warning'
                if final_action == 'Accept':
                    final_action = 'Issue Warning'
            else:  # score > 0.7
                actions[attribute] = 'Reject'
                final_action = 'Reject'
        elif attribute == 'IDENTITY_ATTACK':
            # Low Priority Attribute
            if score < 0.6:
                actions[attribute] = 'Accept'
            elif 0.6 <= score <= 0.8:
                actions[attribute] = 'Issue Warning'
                if final_action == 'Accept':
                    final_action = 'Issue Warning'
            else:  # score > 0.8
                actions[attribute] = 'Reject'
                final_action = 'Reject'
        else:
            # Handle unexpected attributes
            actions[attribute] = 'Accept'

    return final_action, actions


def moderate_post(post_content:str):
    
    #perspective api
    
    attr_scores = perspective(post_content)
    print(attr_scores)
    
    # Actions based on perspective result
    final_action, actions = determine_moderation_action(attr_scores)

    print("Final Action:", final_action)
    print("Actions per Attribute:", actions)
    
    return final_action, actions