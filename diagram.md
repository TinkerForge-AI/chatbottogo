flowchart TD
  %% Authentication & Entry
  A[User Input<br/>(chat UI)] --> B1[API Gateway / FastAPI<br/>Okta Auth]
  B1 --> B2[Network Check<br/>(Wired or VPN)]
  B2 --> C0[Context Gathering]
  
  %% Context Gathering
  C0 --> C0a[Retrieve Conversation History<br/>(MongoDB)]
  C0 --> C0b[Fetch User Profile & Permissions]
  C0 --> C0c[Search Domain Files<br/>(Designated Folder)]
  
  %% Pre-Processing Pipeline
  C0 --> C1[Input Validation]
  C1 --> C1a[Schema Check<br/>(Pydantic)]
  C1 --> C1b[Sanitize Unsafe Characters]
  C1b --> C2[Prompt Injection Defense]
  C2 --> C3[Prompt Framing]
  C3 --> C3a[Apply Dropdown Template]
  C3a --> D[LLM Orchestration Layer]
  
  %% Orchestration & Routing
  D --> D1[Decide LLM Provider]
  D1 -->|External| D2[Open-Source LLM API Adapter]
  D1 -->|Internal| D3[Internal LLM Server Adapter]
  D2 --> E[LLM Call]
  D3 --> E[LLM Call]
  
  %% LLM Backend
  E --> F[Raw LLM Response]
  
  %% Post-Processing Pipeline
  F --> F1[Hallucination & Safety Check]
  F1 --> F2[Markdown Formatting]
  F2 --> F3[Encrypt & Log Conversation]
  
  %% Delivery
  F3 --> G[Send Response<br/>(stream or full)]
  G --> H[User Sees Answer]
  
  %% Notes
  classDef auth fill:#f9f,stroke:#333,stroke-width:1px;
  class B1,B2 auth;
  classDef preprocess fill:#9cf,stroke:#333,stroke-width:1px;
  class C0,C1,C2,C3 preprocess;
  classDef orchestrate fill:#fc9,stroke:#333,stroke-width:1px;
  class D,D1,D2,D3 orchestrate;
  classDef post fill:#c9f,stroke:#333,stroke-width:1px;
  class F,F1,F2,F3 post;