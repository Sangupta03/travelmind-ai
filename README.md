# TRAVELMIND-AI ✈️🌍  
### Agentic AI Travel Planner using Gemini 2.5 Flash

TRAVELMIND-AI is an Agentic AI system that uses multiple autonomous agents to collaboratively design optimized travel itineraries based on user constraints like budget, comfort, walking preference, food habits, and travel companions.

Instead of using a single prompt, TRAVELMIND uses a team of AI agents that negotiate, score, and optimize plans just like a human travel expert team.

---

## 🚀 Features

- Multi-Agent Architecture (User, Budget, Comfort, Experience, Negotiator, Manager)
- Constraint-based planning
- Agent negotiation and arbitration
- Scoring-based optimization
- Explainable AI decisions
- Powered by Gemini 2.5 Flash

---

## 🧠 System Architecture

User → UserAgent → Agent Team → Scoring → Negotiation → Final Optimized Plan

Agents:
- UserAgent → Extracts constraints
- BudgetAgent → Minimizes cost
- ComfortAgent → Maximizes comfort
- ExperienceAgent → Maximizes travel experience
- NegotiatorAgent → Combines best plans
- ManagerAgent → Controls and optimizes everything

---

## 📁 Project Structure

```text
travelmind-ai/
├── agents/
│   ├── user_agent.py
│   ├── budget_agent.py
│   ├── comfort_agent.py
│   ├── experience_agent.py
│   ├── negotiator_agent.py
│   └── manager_agent.py
├── core/
│   ├── llm.py
│   └── scoring.py
├── config.py
├── main.py
├── requirements.txt
└── .env
```
---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

git clone https://github.com/YOUR_USERNAME/travelmind-ai.git

cd travelmind-ai

### 2️⃣ Create Virtual Environment

python -m venv venv
venv\Scripts\activate # Windows


### 3️⃣ Install Dependencies

pip install -r requirements.txt


### 4️⃣ Add Gemini API Key

Create a `.env` file:

GEMINI_API_KEY=your_api_key_here

---

## ▶️ Run the System

python main.py

Example:

Describe your travel needs: Budget trip, vegetarian, low walking, travelling with parents

Destination: Jaipur

Number of days: 3

---

## 📌 Output

- Extracted user constraints
- Multiple candidate plans
- Scored plans
- Final optimized itinerary with reasoning

---

## 🔮 Future Enhancements

- Real flight and hotel APIs
- User memory and personalization
- Failure-aware replanning
- Web dashboard UI
- Mobile app integration

---

## 🏆 Author

Sanjoli Gupta  
