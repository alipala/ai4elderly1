import streamlit as st
import requests
import os
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import io

load_dotenv()

class FinancialAdvisorUI:
    def __init__(self):
        self.api_url = os.getenv("API_URL", "http://localhost:8000")

    def run(self):
        st.title("AI Financial Advisor")
        self.handle_authentication()
        if "token" in st.session_state:
            self.show_profile_management()
            if "profile" in st.session_state:
                tab1, tab2 = st.tabs(["Chat Interface", "Voice Interface"])
                with tab1:
                    self.show_chat_interface()
                with tab2:
                    self.show_voice_interface()
            else:
                st.warning("Please load or create a profile before chatting.")
        else:
            st.warning("Please log in to access the AI Financial Advisor features.")

    def handle_authentication(self):
        if "token" not in st.session_state:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                profile_id = st.text_input("Profile ID (optional)")
                submit_button = st.form_submit_button("Login")
                
                if submit_button:
                    response = requests.post(f"{self.api_url}/token", data={"username": username, "password": password})
                    if response.status_code == 200:
                        st.session_state.token = response.json()["access_token"]
                        st.success("Logged in successfully!")
                        if profile_id:
                            self.load_profile(profile_id)
                        st.experimental_rerun()
                    else:
                        st.error("Invalid credentials")
        else:
            st.success("You are logged in.")
            if st.button("Logout"):
                st.session_state.clear()
                st.experimental_rerun()

    def show_profile_management(self):
        st.header("User Profile")
        
        tab1, tab2, tab3 = st.tabs(["Load Profile", "Create New Profile", "View Stored Profiles"])
        
        with tab1:
            with st.form("load_profile_form"):
                profile_id = st.text_input("Profile ID")
                load_button = st.form_submit_button("Load Profile")
                if load_button:
                    self.load_profile(profile_id)
        
        with tab2:
            with st.form("create_profile_form"):
                st.subheader("Create New Profile")
                name = st.text_input("Name")
                age = st.number_input("Age", min_value=0, max_value=120)
                income = st.number_input("Income", min_value=0.0)
                savings = st.number_input("Savings", min_value=0.0)
                debts = st.number_input("Debts", min_value=0.0)
                investments = st.text_input("Investments")
                financial_goals = st.text_area("Financial Goals (one per line)")
                create_button = st.form_submit_button("Create Profile")
                
                if create_button:
                    self.create_new_profile(name, age, income, savings, debts, investments, financial_goals)
        
        with tab3:
            self.view_stored_profiles()
        
        if "profile" in st.session_state:
            st.subheader("Current Profile")
            st.json(st.session_state.profile)
            
            if st.button("Generate Synthetic Spending Data"):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(f"{self.api_url}/generate_spending_data/{st.session_state.profile['id']}", headers=headers)
                if response.status_code == 200:
                    st.success("Synthetic spending data generated successfully!")
                    self.load_profile(st.session_state.profile['id'])  # Reload the profile to show new data
                else:
                    st.error("Failed to generate synthetic spending data")

    
    def view_stored_profiles(self):
        st.subheader("Stored Profiles")
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{self.api_url}/get_all_profiles", headers=headers)
        if response.status_code == 200:
            profiles = response.json()
            for profile in profiles:
                with st.expander(f"Profile: {profile['name']}"):
                    st.write(f"Profile ID: {profile['id']}")
                    st.write(f"Age: {profile['age']}")
                    st.write(f"Income: {profile['income']}")
                    st.write(f"Savings: {profile['savings']}")
                    st.write(f"Debts: {profile['debts']}")
                    st.write(f"Investments: {profile['investments']}")
                    st.write(f"Financial Goals: {', '.join(profile['financial_goals'])}")
                    if st.button(f"Load Profile {profile['id']}", key=f"load_{profile['id']}"):
                        self.load_profile(profile['id'])
        else:
            st.error("Failed to retrieve stored profiles")   

    def load_profile(self, profile_id):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{self.api_url}/get_profile/{profile_id}", headers=headers)
        if response.status_code == 200:
            st.session_state.profile = response.json()
            st.success("Profile loaded successfully!")
        else:
            st.error("Failed to load profile")

    def create_new_profile(self, name, age, income, savings, debts, investments, financial_goals):
        profile_data = {
            "name": name,
            "age": age,
            "income": income,
            "savings": savings,
            "debts": debts,
            "investments": investments,
            "financial_goals": financial_goals.split('\n') if financial_goals else []
        }
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.post(f"{self.api_url}/create_profile", headers=headers, json=profile_data)
        if response.status_code == 200:
            st.session_state.profile = response.json()
            st.success("Profile created successfully!")
        else:
            st.error("Failed to create profile")

    
    def show_chat_interface(self):
        st.header("Chat with AI Advisor")
        
        # Display conversation history
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = self.get_conversation_history()
        
        chat_history = st.container()
        
        with chat_history:
            for message in st.session_state.conversation_history:
                st.text(f"User: {message['user']}")
                st.text(f"AI: {message['bot']}")
                st.text(f"Timestamp: {message['timestamp']}")
                st.markdown("---")
        
        # Chat input
        with st.form("chat_form_unique", clear_on_submit=True):
            user_input = st.text_input("Your message", key="user_message")
            send_button = st.form_submit_button("Send")
            
            if send_button and user_input:
                if "profile" in st.session_state:
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        data = {"message": user_input}
                        response = requests.post(f"{self.api_url}/chat/{st.session_state.profile['id']}", headers=headers, json=data)
                        if response.status_code == 200:
                            bot_response = response.json()
                            
                            # Update conversation history
                            st.session_state.conversation_history.append({
                                "user": user_input,
                                "bot": bot_response['message'],
                                "timestamp": "Just now"
                            })
                            
                            # Update the chat history display
                            with chat_history:
                                st.text(f"User: {user_input}")
                                st.text(f"AI: {bot_response['message']}")
                                st.text(f"Sentiment: {bot_response['sentiment']} (Confidence: {bot_response['confidence']})")
                                st.markdown("---")
                            
                        else:
                            st.error(f"Failed to get response from AI. Status code: {response.status_code}")
                    except requests.RequestException as e:
                        st.error(f"An error occurred while communicating with the AI: {str(e)}")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")
                else:
                    st.warning("Please load or create a profile before chatting.")

        # Display the latest AI response outside the form
        if st.session_state.conversation_history:
            latest_message = st.session_state.conversation_history[-1]
            st.text(f"Latest AI Response: {latest_message['bot']}")

    def get_conversation_history(self):
        if "profile" in st.session_state:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.get(f"{self.api_url}/conversation_history/{st.session_state.profile['id']}", headers=headers)
            if response.status_code == 200:
                return response.json()
        return []
    
    def show_voice_interface(self):
        st.header("Voice Banking Assistant")
        
        if "voice_auth_setup" not in st.session_state:
            st.session_state.voice_auth_setup = False

        if not st.session_state.voice_auth_setup:
            st.warning("Please set up voice authentication before using the voice assistant.")
            if st.button("Setup Voice Authentication"):
                audio = self.record_audio()
                if audio is not None:
                    success = self.setup_voice_auth(audio)
                    if success:
                        st.session_state.voice_auth_setup = True
                        st.success("Voice authentication set up successfully!")
                    else:
                        st.error("Failed to set up voice authentication. Please try again.")
        else:
            st.success("Voice authentication is set up.")
            if st.button("Speak to Assistant"):
                audio = self.record_audio()
                if audio is not None:
                    self.process_voice_command(audio)

    def record_audio(self, duration=5):
        st.write("Recording... Speak now!")
        audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
        sd.wait()
        return audio.flatten().tobytes()

    def setup_voice_auth(self, audio):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        files = {"audio": ("audio.wav", audio, "audio/wav")}
        url = f"{self.api_url}/voice/setup-voice-auth/{st.session_state.profile['id']}"
        st.write(f"Sending request to: {url}")
        response = requests.post(url, headers=headers, files=files)
        st.write(f"Response status code: {response.status_code}")
        st.write(f"Response content: {response.text}")
        if response.status_code == 200:
            st.success("Voice authentication set up successfully!")
            return True
        else:
            st.error(f"Failed to set up voice authentication: {response.text}")
            return False

    def process_voice_command(self, audio):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        files = {"audio": ("audio.wav", audio, "audio/wav")}
        response = requests.post(f"{self.api_url}/voice/voice-command/{st.session_state.profile['id']}", 
                                headers=headers, files=files)
        if response.status_code == 200:
            result = response.json()
            st.write(f"You said: {result['text']}")
            st.write(f"Assistant: {result['response']}")
            st.write(f"Sentiment: {result['sentiment']} (Confidence: {result['confidence']})")
        else:
            st.error(f"Failed to process voice command: {response.text}")

if __name__ == "__main__":
    financial_advisor_ui = FinancialAdvisorUI()
    financial_advisor_ui.run()