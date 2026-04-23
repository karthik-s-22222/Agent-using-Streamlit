# Detail About Topic
'''# A simple Multi-Agent Customer Support Assistant is an AI system where several specialized AI agents work 
together as a team to solve customer problems more effectively than a single,general-purpose agent could. 
Each agent has a specific role and collaborates with others to handle complex inquiries.'''

#Data
import streamlit as st
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict

#memory
@dataclass
class Memory:
    messages: List[Dict] = field(default_factory=list)
    max_history: int = 500

    def add(self, role, content):
        self.messages.append({"role": role, "content": content, "time": datetime.now().isoformat()})
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def get_context(self):
        return "\n".join([f"{m['role']}: {m['content']}" for m in self.messages[-20:]])

#Intent Agent
class IntentAgent:
    def classify(self, message):
        text = message.lower()
        if "refund" in text: return "refund", "high"
        if "cancel" in text: return "cancellation", "high"
        if "invoice" in text or "bill" in text: return "billing", "medium"
        if "general_Help" in  text or "help" in text: return "help", "low"
        return "replies", "low"
    
#Reply Agent 
class ReplyAgent:
    def create_reply(self, message, intent, urgency):
        replies = {
            "help": "Sure, I'm here to help. Could you please share more details.",
            "refund": "I understand you want a refund. Please share your order ID so I can assist you further.",
            "cancellation": "I can help you cancel your subscription. Kindly provide your registered email.",
            "billing": "It seems you have a billing concern. Please send your invoice number for verification.",
    }
        return replies.get (intent, " How can I assist you today? ")
    
#Escalation Agent
class EscalationAgent:
    def check(self, intent, urgency, message):
        is_high = urgency == "high"
        note = f"Urgent {intent} issue. Needs human review." if is_high else "No escalation required."
        return {"escalate": is_high, "note": note}
    
#Coordinator
class Coordinator:
    def __init__(self):
        self.intent_agent = IntentAgent()
        self.reply_agent = ReplyAgent()
        self.escalation_agent = EscalationAgent()
        self.memory = Memory()

    def ask(self, message):
        self.memory.add("user", message)
        intent, urgency = self.intent_agent.classify(message)
        reply = self.reply_agent.create_reply(message, intent, urgency)
        escalation = self.escalation_agent.check(intent, urgency, message)
        self.memory.add("agent", reply)

        return {
            "timestamp": datetime.now().isoformat(),
            "intent": intent,
            "urgency": urgency,
            "reply": reply,
            "escalate": escalation["escalate"]
        }
st.set_page_config(page_title="AI Support Bot", page_icon="📶", layout="centered")

st.markdown("""
    <style>
    .menu-container {
        background-color: #6A5ACD;
        padding: 10px;
        border-radius: 100px;
        border: 1px solid #483d8b;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

if "user_message" not in st.session_state:
    st.session_state.user_message = Coordinator()
    st.toast("👋 Welcome! How can we help you today?")

st.set_page_config( page_title=" AI Bot ", page_icon="📶")
st.title("💭 Customer Support Bot")

with st.container():
    st.markdown('<div class="menu-container">', unsafe_allow_html=True)
    st.write("**Suggestion Menu**")
    cols = st.columns(4)

    menu_options = {
        "invoice": "💳",
        "Refund": "💰",
        "Cancel": "❌",
        "Help": "🆘"
        
    }
    
    clicked_suggestion = None

    for i, (label, icon) in enumerate(menu_options.items()):
        if cols[i].button(f"{icon} {label}", use_container_width=True):
            clicked_suggestion = label
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")   


prompt = final_prompt if (final_prompt := st.chat_input("How can I help you today?")) else clicked_suggestion

for msg in st.session_state.user_message.memory.messages:
    role = "assistant" if msg["role"] == "agent" else "user"
    with st.chat_message(role):
        st.write(msg["content"])


if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    response = st.session_state.user_message.ask(prompt)

    with st.chat_message("assistant"):
        st.write(response["reply"])
        if response.get('escalate'):
            st.warning("[Note: your request will proceed further for human review]")

if st.session_state.get('show_exit_toast'):
    st.toast("Thank you! Session closed successfully.", icon="👋")
    st.session_state.show_exit_toast = False

st.sidebar.markdown("---")
if st.sidebar.button("🔚 End Session", use_container_width=True):
    st.toast("Thank you! Closing your session...", icon="👋")
    st.session_state.user_message = Coordinator()
    st.session_state.show_exit_toast = True
    st.rerun()