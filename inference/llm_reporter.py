import threading
import requests
import json
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")

def _call_openai_api(payload, frame_id, tech_str):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        vote_percent = round(payload['vote'] * 100, 1)
        prompt = f"Write a professional 2-sentence police incident dispatch report for a CCTV detection. Time/Frame: {frame_id}, Confidence: {vote_percent}%. Suspected Technique: {tech_str}. Suspect ID: {payload['track_id_1']}, Victim ID: {payload['track_id_2']}."
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a professional security dispatch AI."}, 
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            report_text = response.json()['choices'][0]['message']['content'].strip()
            
            os.makedirs('outputs/logs', exist_ok=True)
            with open(f"outputs/logs/incident_report_{frame_id}.txt", "w") as f:
                f.write(report_text)
            print(f"\n[Generative AI] Incident Report generated successfully for Frame {frame_id}!")
        else:
            print(f"\n[Generative AI Failsafe] API call failed with status: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"\n[Generative AI Failsafe] Caught exception while contacting OpenAI: {e}")

def trigger_llm_report_async(payload, frame_id, tech_str):
    """
    Triggers the OpenAI API call in a background thread to prevent crashing or stalling 
    the main cv2 video loop.
    """
    t = threading.Thread(target=_call_openai_api, args=(payload, frame_id, tech_str))
    t.daemon = True
    t.start()
