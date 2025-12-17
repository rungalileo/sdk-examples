# Galileo Chatbot

A full-stack chatbot application with a Java Spring Boot backend and Next.js frontend, supporting multiple AI providers including Azure OpenAI and Mistral AI, with integrated RAG (Retrieval Augmented Generation) capabilities and Galileo observability for monitoring and logging all interactions.

## Architecture

- **Backend**: Java Spring Boot (port 8080)
- **Frontend**: Next.js with React (port 3000)
- **AI Services**: 
  - Azure OpenAI (GPT-5-nano)
  - Mistral AI (mistral-medium, mistral-small, mistral-tiny, mistral-large-latest)
- **RAG (Retrieval Augmented Generation)**: In-memory vector store with semantic search using Mistral embeddings (with automatic fallback to Azure OpenAI on rate limits)
- **Observability**: Galileo AI v2 API for session management, trace logging, and Protect security checks
- **Security**: Galileo Protect integration for input/output validation and content moderation

## Prerequisites

- Java 17
- Maven 3.6
- Node.js 18 and npm
- Azure OpenAI account with deployment, such as for GPT-5-nano (for Azure provider)
- Mistral AI API key (for Mistral provider) - Get one at [https://console.mistral.ai/](https://console.mistral.ai/)
- Galileo AI account with API key, project ID, and log stream ID (for observability) - Get one at [https://console.galileo.ai/](https://console.galileo.ai/)

## Setup Instructions

### 1. Backend Setup

1. Configure AI provider credentials in `src/main/resources/application.properties`:

   **Azure OpenAI Configuration:**
   ```properties
   azure.openai.endpoint=https://YOUR_RESOURCE_NAME.openai.azure.com
   azure.openai.api-key=YOUR_API_KEY
   azure.openai.deployment-name=gpt-5-nano
   azure.openai.embedding-deployment-name=text-embedding-ada-002
   ```
   
   Note: The embedding deployment is used as a fallback for RAG functionality when Mistral embeddings hit rate limits.

   **Mistral AI Configuration:**
   ```properties
   mistral.api-key=YOUR_MISTRAL_API_KEY
   mistral.model=mistral-medium
   ```
   
   Available Mistral models:
   - `mistral-tiny` (fastest, cheapest)
   - `mistral-small`
   - `mistral-medium` (default)
   - `mistral-large-latest` (most capable)

   **Galileo AI Configuration (Optional but recommended):**
   ```properties
   galileo.api-key=YOUR_GALILEO_API_KEY
   galileo.api-url=https://api.demo-v2.galileocloud.io/
   galileo.project-name=YOUR_PROJECT_NAME
   galileo.project-id=YOUR_PROJECT_ID
   galileo.log-stream-id=YOUR_LOG_STREAM_ID
   galileo.stage-name=YOUR_STAGE_NAME
   galileo.stage-id=YOUR_STAGE_ID
   galileo.stage-version=0
   ```
   
   Note: 
   - If Galileo logging is not configured, the application will run without observability logging
   - If Galileo Protect is not configured (missing `stage-name`), Protect checks will be skipped
   - To get your project ID and log stream ID:
     1. Log into your Galileo console
     2. Navigate to your project
     3. Create or select a log stream
     4. Copy the project ID and log stream ID from the URLs or project settings
   - To configure Protect, create a stage in the Galileo console and copy the stage name and ID using the protect_stage_setup/create_stage, making sure to update the project id.

2. Build and run the backend:
   ```bash
   mvn clean install
   mvn spring-boot:run
   ```

   The backend will start on `http://localhost:8080`

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

   The frontend will start on `http://localhost:3000`

## Usage

1. Start the backend server (port 8080)
   - A Galileo session will be automatically created when the app starts
   - Check the console logs for "Galileo session created with ID: ..."
2. Start the frontend server (port 3000)
3. Open `http://localhost:3000` in your browser
4. Select your preferred AI provider (Azure OpenAI or Mistral AI) from the dropdown
5. Start chatting with the Galileo Chatbot!
   - Every input/output pair is automatically logged to Galileo as a trace
   - All traces are grouped under the same session
   - Responses are limited to 30 words or less
   - The chatbot uses RAG to retrieve relevant context from ingested documents
6. When you shut down the app, the session will be automatically closed

### Request Flow

For each chat message, the following steps occur:

1. **Document Retrieval** (RAG)
   - Query is embedded using Mistral embeddings (or Azure if rate limited)
   - Top 3 most relevant document chunks are retrieved via cosine similarity
   - Retriever span is created and logged

2. **LLM Call**
   - Retrieved context is added to the system prompt
   - Chat completion is requested from the selected provider (Azure or Mistral)
   - LLM span is created and logged

3. **Protect Output Check**
   - LLM response is validated by Galileo Protect
   - Checks for prompt injection, PII, and context adherence
   - If violations detected, response is overridden with safe message
   - Original response is preserved in metadata
   - Protect tool span is created and logged

4. **Trace Logging**
   - All spans (retriever, LLM, Protect) are logged together as a single trace
   - Trace includes metadata: tokens, duration, probabilities, etc.

### RAG Features

- **Pre-loaded Document**: The knowledge base comes with the AI EU Act summary document loaded from `ai_eu_act_summary.pdf` in the resources folder
- **Semantic Search**: The chatbot automatically retrieves the top 3 most relevant document chunks for each query
- **Context-Aware Responses**: Retrieved context is included in the system prompt to provide accurate, relevant answers
- **30-Word Limit**: All responses are constrained to 30 words or less for concise answers
- **Embedding Service**: Uses Mistral `mistral-embed` model for generating embeddings
- **Automatic Fallback**: If Mistral embeddings hit rate limits (429), automatically falls back to Azure OpenAI embeddings

### Observability Features

- **Automatic Session Management**: A new session is created when the app starts and closed when it shuts down
  - Sessions are protected against duplicate creation (e.g., from Spring DevTools auto-restart)
  - One session per application lifecycle
- **Trace Logging**: Every chat interaction (input/output pair) is logged as a separate trace to Galileo
- **Session Grouping**: All traces within an app session are grouped together for easy analysis
- **Span Hierarchy**: Each trace includes child spans in the following order:
  1. **Retriever Span**: Document retrieval step (independent, created first)
  2. **LLM Span**: Chat completion call
  3. **Protect Tool Span**: Security/content moderation check (output validation)
- **Metadata Tracking**: Each trace includes:
  - Input and output content
  - Provider (Azure OpenAI or Mistral AI)
  - Model name
  - Token counts (estimated)
  - Duration in nanoseconds
  - Timestamp
  - Original LLM response (if Protect overrides the output)
  - Protect probability scores (context adherence, etc.)

### Security Features (Galileo Protect)

- **Output Validation**: All LLM responses are checked by Galileo Protect before being returned to the user
- **Content Moderation**: Protect checks for:
  - Prompt injection attempts
  - PII (Personally Identifiable Information) in inputs
  - Context adherence (ensuring responses align with retrieved documents)
- **Automatic Override**: If Protect detects violations, the response is replaced with a safe override message
- **Original Response Preservation**: The original LLM response is preserved in metadata even when overridden
- **Tool Span Logging**: Each Protect invocation is logged as a tool span with:
  - Request payload (input, output, context)
  - Response status and metrics
  - Probability scores
  - Override actions taken

## API Endpoints

### POST `/api/chat`

Send a chat message to the bot.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "history": ["previous messages..."],
  "provider": "azure"
}
```

**Parameters:**
- `message` (required): The user's message
- `history` (optional): Array of previous conversation messages for context
- `provider` (optional): AI provider to use - `"azure"` or `"mistral"` (defaults to `"azure"`)

**Response:**
```json
{
  "response": "I'm doing well, thank you for asking!"
}
```

## Project Structure

```
.
├── src/
│   └── main/
│       ├── java/com/chatbot/
│       │   ├── ChatbotApplication.java
│       │   ├── config/
│       │   │   ├── WebConfig.java
│       │   │   ├── GalileoSessionManager.java
│       │   │   └── DocumentInitializer.java
│       │   ├── controller/
│       │   │   └── ChatController.java
│       │   ├── service/
│       │   │   ├── AzureOpenAIService.java
│       │   │   ├── MistralService.java
│       │   │   ├── GalileoService.java
│       │   │   ├── EmbeddingService.java
│       │   │   ├── VectorStoreService.java
│       │   │   └── DocumentService.java
│       │   └── dto/
│       │       ├── ChatRequest.java
│       │       ├── ChatResponse.java
│       │       └── ChatCompletionResult.java
│       └── resources/
│           └── application.properties
├── frontend/
│   ├── app/
│   │   ├── components/
│   │   │   └── ChatInterface.tsx
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── package.json
│   └── tsconfig.json
└── pom.xml
```

## Technologies Used

- **Backend**: Spring Boot, Azure OpenAI SDK, RestTemplate (for Mistral AI and Galileo API)
- **Frontend**: Next.js 14, React 18, TypeScript
- **Build Tools**: Maven, npm
- **AI Providers**: Azure OpenAI, Mistral AI
- **RAG**: In-memory vector store with cosine similarity search, Mistral embeddings (with Azure OpenAI fallback)
- **Observability**: Galileo AI v2 API for session management, trace logging, and Protect security checks
- **Security**: Galileo Protect for content moderation and output validation
- **PDF Processing**: Apache PDFBox for document text extraction
- **JSON Processing**: Jackson (ObjectMapper) for API response parsing

