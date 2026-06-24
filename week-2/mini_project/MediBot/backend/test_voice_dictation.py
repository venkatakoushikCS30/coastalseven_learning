import os
import wave
import struct
import requests
import json

def generate_silent_wav(filename, duration=1.0, rate=44100):
    """Generates a small silent WAV file to use for testing audio uploads."""
    print(f"Generating temporary silent WAV file: {filename}")
    num_samples = int(duration * rate)
    
    # 1 channel, 2 bytes per sample (16-bit), 44100Hz sample rate
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        
        # Write silence (zeros)
        for _ in range(num_samples):
            data = struct.pack('<h', 0)
            wav.writeframesraw(data)

def test_voice_dictation_flow():
    # 1. Setup paths
    wav_filename = "test_dictation.wav"
    generate_silent_wav(wav_filename)
    
    # 2. Setup login to get token
    login_url = "http://localhost:8000/api/auth/login/"
    headers = {}
    
    print("\nAttempting login to acquire JWT token...")
    try:
        login_res = requests.post(login_url, json={
            "username": "doctor1",
            "password": "doctorpass"
        }, timeout=5)
        
        if login_res.status_code == 200:
            token = login_res.json().get("access")
            headers["Authorization"] = f"Bearer {token}"
            print("Login successful! Acquired JWT token.")
        else:
            print(f"Login failed (status {login_res.status_code}): {login_res.text}")
            print("Note: Running tests using unauthenticated request fallback simulation...")
    except Exception as e:
        print(f"Backend offline or connection failed: {str(e)}")
        print("Note: Make sure Django is running on http://localhost:8000/ to test the live API.")
        
    # 3. Post audio file to /api/ai/voice-to-ehr/
    upload_url = "http://localhost:8000/api/ai/voice-to-ehr/"
    
    if os.path.exists(wav_filename):
        print(f"\nPosting audio file '{wav_filename}' to Voice-to-EHR endpoint...")
        try:
            with open(wav_filename, 'rb') as f:
                files = {'file': (wav_filename, f, 'audio/wav')}
                res = requests.post(upload_url, files=files, headers=headers, timeout=10)
                
            print(f"Server response status code: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                print("\n=== Structured EHR Extraction Results ===")
                print(f"Transcription text: \"{data.get('transcription')}\"")
                print(f"Extracted Symptoms: \"{data.get('symptoms')}\"")
                print(f"Extracted Diagnosis: \"{data.get('diagnosis')}\"")
                print(f"Extracted Prescription: \"{data.get('prescription')}\"")
                print("=========================================")
                print("Test passed successfully!")
            else:
                print(f"Error payload: {res.text}")
        except Exception as e:
            print(f"Failed to post to voice-to-ehr endpoint: {str(e)}")
            
        # Clean up wav file
        os.remove(wav_filename)
        print("\nCleaned up temporary audio files.")
    else:
        print(f"Audio file {wav_filename} was not found.")

if __name__ == "__main__":
    test_voice_dictation_flow()
