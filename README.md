# 🧠 NeuraCRM  
**Conversational intelligence meets automated CRM workflows.**


## ✨ Inspiration

We built NeuraCRM for anyone who’s ever ended a call and thought:  
*“Wait, did anyone actually log what we promised the client?”*

CRM systems were designed to keep teams organized, but in practice, they’re often an afterthought—updated only after back-to-back meetings, fueled by fading memory and guesswork. Meanwhile, high-stakes conversations unfold in real time, full of action items, risks, and follow-ups that don’t always make it to the system.

**NeuraCRM is our answer to that gap**: an AI-powered assistant that listens in, thinks alongside you, and acts for you.

Built during a hackathon, but envisioned for a world where AI doesn’t just observe—it participates.


## 🧩 What It Does

NeuraCRM brings structure and intelligence to every customer-facing conversation, transforming live dialogue into actionable data:

- **Real-Time Transcription**  
  Captures and transcribes calls with low latency, forming the base context for downstream tasks.

- **Conversational AI Insights**  
  Understands context mid-call to answer queries like *“What’s their contract value?”* or *“Any blockers mentioned last time?”*

- **Follow-Up Nudges**  
  Suggests useful next steps—*“Want to ask about renewal?”*—based on the call’s flow.

- **Task Generation**  
  Extracts action items like *“send a quote”* or *“file a support ticket”* and pushes them to tools like **Jira** or drafts follow-ups in **Gmail**.

- **Flexible Integration Model**  
  While Jira and Gmail are supported out-of-the-box, the backend is designed for quick extension to Slack, Trello, knowledge bases, and internal tools.


## ⚙️ How It Works

Under the hood, NeuraCRM brings together real-time streams, intelligent decision-making, and action execution:

- **Speech Recognition** — Powered by Azure STT, feeding transcript chunks live into the system.
- **LLM Orchestration** — GPT-4, guided by LangChain chains, processes context and determines next steps.
- **Hybrid Search** — Combines Neo4j’s graph traversal with embedding-based semantic similarity for relevant memory recall.
- **Tool Use & Execution** — LangChain Agents manage structured actions, converting user intent into real API calls.
- **Real-Time Event Architecture** — A Flask + Socket.IO backend ensures low-latency bi-directional communication between frontend and backend.


## 🧑‍💼 Built For

NeuraCRM supports a range of roles and workflows:

- **Sales Teams & Account Managers**  
  Focus on the client; let NeuraCRM remember the details and log them for you.

- **Customer Support Reps**  
  Reduce time hunting through docs—get answers, create tickets, and send follow-ups effortlessly.

- **CRM Engineers & Developers**  
  Looking to add AI into existing systems? NeuraCRM shows how to combine language models with graph queries, tools, and actions.

- **AI Tool Builders**  
  Learn how to chain real-time transcription with multi-modal actions. This is a working prototype of what's possible at the frontier of CRM + AI.


## 🛠️ Built With

- **OpenAI GPT-4** — Context-aware reasoning and content generation.
- **LangChain** — LLM chaining, routing, and agent-based tool usage.
- **Neo4j** — Knowledge graph for structured CRM context and hybrid semantic search.
- **Azure STT** — Streaming speech-to-text engine with speaker tracking.
- **Flask + Socket.IO** — Event-driven backend for low-latency data flow.
- **Jira & Gmail APIs** — Task creation, email follow-ups, and assistant-driven action.


## 💡 Why This Matters

NeuraCRM isn’t just a product—it's a simple blueprint.

It’s a concept for CRM systems that don’t lag behind the conversation. That react when needed. That log and act automatically. And that keep humans in the loop—but not in the weeds.

In a future where every team has its own co-pilot, tools like this will be the norm—not the novelty.


## 🎓 What We Learned

- **Prompt Engineering is strategy** — Good prompts don’t just work, they orchestrate.
- **Modularity scales better** — Breaking AI systems into distinct decision, retrieval, and action blocks made development faster and easier.
- **Timing is UX** — Being responsive without being premature was one of the biggest challenges in handling real-time data streams.
- **Agents are underrated** — Once properly structured, LangChain’s agents opened doors to smooth integrations and low-code expansions.


## 🚀 Running NeuraCRM (Modular Version)

> ⚠️ *Note: This project is still a work in progress.*

### 🔧 Prerequisites

- Python 3.10+
- Node.js & npm (for frontend)
- Virtual environment tool (e.g., `venv` or `conda`)
- OpenAI API Key
- Neo4j instance (local or Aura)
- Azure Speech API Key + Region
- Jira and Gmail developer credentials (optional)


### 🛠 Backend Setup

#### Clone the repository and set up the virtual environment
```bash
git clone URL
cd neuracrm
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

#### Create .env file inside App/server/
```bash
mkdir -p App/server
cat <<EOF > App/server/.env
OPENAI_API_KEY=your-key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
SPEECH_KEY=your-azure-key
SPEECH_REGION=your-region
JIRA_EMAIL=your-email
JIRA_API_KEY=your-jira-key
EOF
```

#### Run the backend server
```bash
cd App/server
python main.py
```

#### Open a new terminal for the frontend setup or run in background if needed

#### Setup and run frontend
```bash
cd ../client
npm install
npm run dev
```
