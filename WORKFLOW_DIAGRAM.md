# Workflow Execution Diagram

## Component Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        WORKFLOW BUILDER                         │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ User Query   │───▶│ Knowledge    │───▶│ LLM Engine   │    │
│  │ Component    │    │ Base         │    │              │    │
│  └──────────────┘    └──────────────┘    └──────┬───────┘    │
│                                                  │            │
│                                                  ▼            │
│                                            ┌──────────────┐   │
│                                            │   Output     │   │
│                                            │  Component   │   │
│                                            └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Execution Flow

### 1. User Query Component
```
User Input
    │
    ▼
┌───────────────┐
│ User Query    │  Entry point
│ Component     │  - Receives user query
│               │  - Validates input
└───────┬───────┘
        │
        │ Passes query forward
        ▼
```

### 2. Knowledge Base Component (Optional)
```
        │
        ▼
┌───────────────────────┐
│ Knowledge Base        │
│ Component             │
│                       │
│ 1. Generate Query     │
│    Embedding          │
│                       │
│ 2. Vector Search      │
│    in ChromaDB        │
│                       │
│ 3. Retrieve Top K     │
│    Relevant Chunks    │
│                       │
│ 4. Combine Context    │
└───────┬───────────────┘
        │
        │ Query + Context
        ▼
```

### 3. LLM Engine Component
```
        │
        ▼
┌───────────────────────┐
│ LLM Engine            │
│ Component             │
│                       │
│ ┌──────────────────┐  │
│ │ Optional:        │  │
│ │ Web Search       │  │
│ │ (SerpAPI/Brave)  │  │
│ └────────┬─────────┘  │
│          │            │
│ ┌────────▼─────────┐  │
│ │ Combine:        │  │
│ │ - Query         │  │
│ │ - Context       │  │
│ │ - Web Results   │  │
│ │ - Custom Prompt │  │
│ └────────┬─────────┘  │
│          │            │
│ ┌────────▼─────────┐  │
│ │ LLM Generation   │  │
│ │ (OpenAI/Gemini)  │  │
│ └────────┬─────────┘  │
└──────────┼────────────┘
           │
           │ Generated Response
           ▼
```

### 4. Output Component
```
           │
           ▼
┌───────────────────────┐
│ Output Component      │
│                       │
│ - Display Response    │
│ - Chat Interface      │
│ - Maintain History    │
└───────────────────────┘
```

## Data Flow Example

### Example: Document Q&A Workflow

```
1. User Query: "What is machine learning?"
   │
   ▼
2. User Query Component
   Output: { query: "What is machine learning?" }
   │
   ▼
3. Knowledge Base Component
   - Embed query
   - Search in ChromaDB
   - Retrieve top 5 relevant chunks
   Output: { 
     query: "What is machine learning?",
     context: "Machine learning is a subset of AI..."
   }
   │
   ▼
4. LLM Engine Component
   - Combine query + context
   - Generate response with GPT-3.5
   Output: {
     query: "What is machine learning?",
     context: "...",
     response: "Machine learning is a subset of artificial intelligence..."
   }
   │
   ▼
5. Output Component
   Display: "Machine learning is a subset of artificial intelligence..."
```

## Component Configuration

### Knowledge Base Component
```
Configuration:
├── Knowledge Base ID: "my_documents"
├── Embedding Model: "openai" | "gemini"
└── Top K Results: 5
```

### LLM Engine Component
```
Configuration:
├── LLM Provider: "openai" | "gemini"
├── Model: "gpt-3.5-turbo" | "gpt-4" | "gemini-pro"
├── Custom Prompt: (optional)
├── Use Web Search: true | false
└── Web Search Provider: "serpapi" | "brave"
```

## Error Handling

```
┌──────────────┐
│   Error      │
│   Occurs     │
└──────┬───────┘
       │
       ├──▶ Validation Error
       │    └──▶ Return error message
       │
       ├──▶ API Error
       │    └──▶ Log error, return fallback
       │
       └──▶ Execution Error
            └──▶ Log error, return error response
```

## State Management

```
Workflow State:
├── Nodes: [Component definitions]
├── Edges: [Connections between components]
├── Config: [Component configurations]
└── Status: "draft" | "saved" | "active"

Chat State:
├── Session ID: UUID
├── Messages: [History]
├── Current Query: String
└── Loading: Boolean
```
