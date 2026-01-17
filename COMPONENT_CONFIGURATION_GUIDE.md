# Component Configuration Guide

This guide explains what to enter in each configuration field for all workflow components.

## 1. User Query Component

### Component Name
- **What it is**: A display name for this component
- **What to enter**: Any text you want (e.g., "User Query", "Input", "Question Entry")
- **Example**: `User Query`
- **Required**: No (defaults to "User Query")
- **Note**: This is just for labeling; it doesn't affect functionality

---

## 2. Knowledge Base Component

### Knowledge Base ID
- **What it is**: A unique identifier for your document collection
- **What to enter**: 
  - A unique name/ID for your knowledge base (e.g., `my_documents`, `company_kb`, `product_manual`)
  - Use the SAME ID when uploading documents via the API
- **Example**: `my_documents`
- **Required**: Yes (if using Knowledge Base component)
- **How to get it**: 
  1. Choose any name you want
  2. Use this same name when uploading documents:
     ```bash
     curl -X POST "http://localhost:8000/api/documents/upload" \
       -F "file=@document.pdf" \
       -F "knowledge_base_id=my_documents"
     ```

### Embedding Model
- **What it is**: Which AI service to use for creating embeddings (vector representations)
- **Options**:
  - `OpenAI` - Uses OpenAI's embedding model (requires OPENAI_API_KEY)
  - `Gemini` - Uses Google Gemini's embedding model (requires GOOGLE_API_KEY)
- **What to enter**: Select from dropdown
- **Example**: Choose `Gemini` if you only have Google API key
- **Required**: Yes
- **Note**: Must match the API key you have configured in your `.env` file

### Top K Results
- **What it is**: How many relevant document chunks to retrieve
- **What to enter**: A number between 1 and 20
- **Example**: `5` (recommended)
- **Default**: `5`
- **Required**: No
- **Recommendation**: 
  - `3-5` for focused answers
  - `5-10` for comprehensive answers
  - `10+` for very detailed context (may be slower)

---

## 3. LLM Engine Component

### LLM Provider
- **What it is**: Which AI language model service to use
- **Options**:
  - `OpenAI GPT` - Uses OpenAI models (requires OPENAI_API_KEY)
  - `Google Gemini` - Uses Google Gemini (requires GOOGLE_API_KEY)
- **What to enter**: Select from dropdown
- **Example**: Choose `Google Gemini` if you only have Google API key
- **Required**: Yes
- **Note**: Must match the API key you have configured

### Model (only shown when OpenAI is selected)
- **What it is**: Which OpenAI model to use
- **Options**:
  - `GPT-3.5 Turbo` - Fast, cost-effective (recommended for most use cases)
  - `GPT-4` - More capable, slower, more expensive
  - `GPT-4 Turbo` - Latest GPT-4, faster than GPT-4
- **What to enter**: Select from dropdown
- **Example**: `GPT-3.5 Turbo`
- **Required**: Yes (when OpenAI is selected)
- **Note**: Not shown when Gemini is selected (uses gemini-pro automatically)

### Custom Prompt (Optional)
- **What it is**: A custom system prompt to guide the AI's behavior
- **What to enter**: 
  - Instructions for how the AI should respond
  - Leave empty to use default behavior
- **Examples**:
  ```
  You are a helpful customer support assistant. Always be polite and professional.
  ```
  ```
  You are an expert in machine learning. Explain concepts clearly with examples.
  ```
  ```
  Answer questions based only on the provided context. If the answer is not in the context, say "I don't have that information."
  ```
- **Required**: No
- **Best practices**:
  - Be specific about the AI's role
  - Include tone/style preferences
  - Set boundaries (e.g., "only use provided context")

### Enable Web Search
- **What it is**: Whether to search the web for additional information
- **What to enter**: Check the box to enable, uncheck to disable
- **Example**: Check the box if you want current information from the internet
- **Required**: No (defaults to unchecked)
- **When to use**:
  - ✅ Enable: Questions about current events, recent news, real-time data
  - ❌ Disable: Questions about uploaded documents, general knowledge, faster responses

### Web Search Provider (only shown when Web Search is enabled)
- **What it is**: Which web search service to use
- **Options**:
  - `SerpAPI` - Requires SERPAPI_API_KEY
  - `Brave Search` - Requires BRAVE_API_KEY
- **What to enter**: Select from dropdown
- **Example**: `SerpAPI`
- **Required**: Yes (if Web Search is enabled)
- **Note**: You need at least one API key configured in your `.env` file

---

## 4. Output Component

### Component Name
- **What it is**: A display name for this component
- **What to enter**: Any text you want (e.g., "Output", "Response", "Answer")
- **Example**: `Output`
- **Required**: No (defaults to "Output")
- **Note**: This is just for labeling; it doesn't affect functionality

---

## Complete Configuration Examples

### Example 1: Simple Q&A (OpenAI only)
```
User Query Component:
  Component Name: "User Query"

LLM Engine Component:
  LLM Provider: "OpenAI GPT"
  Model: "GPT-3.5 Turbo"
  Custom Prompt: (leave empty)
  Enable Web Search: (unchecked)

Output Component:
  Component Name: "Output"
```

### Example 2: Document Q&A with Gemini
```
User Query Component:
  Component Name: "User Query"

Knowledge Base Component:
  Knowledge Base ID: "my_documents"
  Embedding Model: "Gemini"
  Top K Results: 5

LLM Engine Component:
  LLM Provider: "Google Gemini"
  Custom Prompt: "Answer based on the provided context. Be concise."
  Enable Web Search: (unchecked)

Output Component:
  Component Name: "Output"
```

### Example 3: Web-Enhanced Q&A
```
User Query Component:
  Component Name: "User Query"

LLM Engine Component:
  LLM Provider: "OpenAI GPT"
  Model: "GPT-3.5 Turbo"
  Custom Prompt: "Provide current and accurate information."
  Enable Web Search: ✓ (checked)
  Web Search Provider: "SerpAPI"

Output Component:
  Component Name: "Output"
```

### Example 4: Full Stack (Documents + Web Search)
```
User Query Component:
  Component Name: "User Query"

Knowledge Base Component:
  Knowledge Base ID: "company_docs"
  Embedding Model: "OpenAI"
  Top K Results: 7

LLM Engine Component:
  LLM Provider: "OpenAI GPT"
  Model: "GPT-4"
  Custom Prompt: "Use the provided context first. If information is missing, supplement with web search results."
  Enable Web Search: ✓ (checked)
  Web Search Provider: "Brave Search"

Output Component:
  Component Name: "Response"
```

---

## Quick Reference

| Component | Field | Required | Example Value |
|-----------|-------|----------|---------------|
| User Query | Component Name | No | "User Query" |
| Knowledge Base | Knowledge Base ID | Yes | "my_documents" |
| Knowledge Base | Embedding Model | Yes | "Gemini" |
| Knowledge Base | Top K Results | No | 5 |
| LLM Engine | LLM Provider | Yes | "Google Gemini" |
| LLM Engine | Model | Yes* | "GPT-3.5 Turbo" |
| LLM Engine | Custom Prompt | No | (optional text) |
| LLM Engine | Enable Web Search | No | (checkbox) |
| LLM Engine | Web Search Provider | Yes** | "SerpAPI" |
| Output | Component Name | No | "Output" |

*Only when OpenAI is selected
**Only when Web Search is enabled

---

## Common Mistakes to Avoid

1. **Knowledge Base ID Mismatch**: 
   - ❌ Wrong: Upload document with `knowledge_base_id="docs"` but configure component with `"my_docs"`
   - ✅ Correct: Use the same ID everywhere

2. **API Key Mismatch**:
   - ❌ Wrong: Set Embedding Model to "Gemini" but only have OPENAI_API_KEY
   - ✅ Correct: Match the model/provider with your available API keys

3. **Missing Required Fields**:
   - ❌ Wrong: Leave Knowledge Base ID empty when using Knowledge Base component
   - ✅ Correct: Always fill required fields

4. **Web Search Without API Key**:
   - ❌ Wrong: Enable Web Search but don't have SERPAPI_API_KEY or BRAVE_API_KEY
   - ✅ Correct: Only enable if you have the corresponding API key

---

## Need Help?

- Check your `.env` file for API keys
- Verify API keys are valid and have credits/quota
- Test with simple workflows first
- Check browser console for errors
- Review backend logs for API errors
