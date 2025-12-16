🤖 ChatGPT Usage Transparency

This project was developed with the assistance of AI tools (ChatGPT and GitHub Copilot) as productivity and reasoning aids, not as autonomous code generators. AI was used to support design clarification, architectural planning, debugging guidance, and documentation drafting, while all final implementation decisions, code integration, testing, and validation were performed manually by the developer.

AI assistance helped accelerate understanding and iteration but did not replace core engineering judgment, especially in areas such as data alignment, statistical correctness, and real-time system stability.

🔹 How AI Was Used

AI tools were used in the following ways:

Clarifying the problem statement and expectations of the quant analytics assignment

Designing a clean system architecture (ingestion → storage → analytics → API → frontend → alerts)

Proposing a simple, realistic tech stack suitable for a 1-day prototype

Debugging complex issues related to NaN propagation, time-series alignment, and chart stability

Refining analytics logic (OLS hedge ratio, spread, Z-score, correlation, ADF test)

Drafting documentation and demo explanations

AI was not used to blindly generate final code. All AI-generated suggestions were reviewed, modified, and validated against real-time data behavior.

🧠 Prompts Used During Development

The following are representative prompts used while building the project:

1️⃣ Understanding the Assignment
Explain the goal of a real-time quantitative analytics dashboard using live Binance WebSocket data. 
What analytics are typically expected in a pairs trading or statistical arbitrage context?

2️⃣ System Architecture Design
Design a modular system architecture for a real-time quantitative analytics platform that includes:
data ingestion, storage, resampling, analytics, API layer, frontend dashboard, and alerts.
Explain how data flows through the system.

3️⃣ Tech Stack Selection
Suggest a simple, Python-first tech stack for building a real-time quant analytics prototype
with live data ingestion, statistical analysis, and interactive visualization.

4️⃣ Quantitative Analytics Validation
Explain how OLS hedge ratio, spread, rolling Z-score, rolling correlation, 
and ADF stationarity test are used in pairs trading.
What are common pitfalls with intraday data?

5️⃣ Debugging NaN and Time-Series Issues
Why do rolling statistics like z-score and correlation often produce NaN values 
in real-time systems? How should aligned time-series data be handled safely 
before visualization?

6️⃣ Frontend Stability & Visualization
Why do charting libraries crash when receiving empty or invalid data?
How should a frontend guard against rendering charts before data is ready?

7️⃣ Architecture Diagram Generation
Create a system architecture diagram showing Binance WebSocket ingestion, 
data storage, resampling, analytics engine, FastAPI backend, React frontend, 
and alert flow for a real-time quantitative analytics dashboard.

8️⃣ Documentation & Demo Preparation
Write a concise README explaining how a real-time quantitative analytics dashboard works,
including setup, analytics, and design philosophy.