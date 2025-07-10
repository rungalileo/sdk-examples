import { GalileoLogger } from "galileo-experimental";

const logger = new GalileoLogger();

// Start a trace for a RAG application
const trace = logger.startTrace({
  input: "What were the major causes of World War I?",
  metadata: {
    user_id: "123",
    session_id: "456",
    timestamp: new Date().toISOString(),
  },
});

// Start a workflow span for the retrieval process
const retrievalWorkflow = trace.startWorkflowSpan("Document Retrieval");

// Add a retriever span for the query
retrievalWorkflow.logRetrieverSpan(
  "What were the major causes of World War I?",
  [
    { content: "The assassination of Archduke Franz Ferdinand...", metadata: { source: "history.txt" } },
    { content: "Militarism, alliances, imperialism, and nationalism...", metadata: { source: "causes.txt" } }
  ]
);

// End the retrieval workflow
retrievalWorkflow.end("Retrieved 2 documents");

// Add an LLM span for generating the response
trace.logSpan(
  "Based on these documents, what were the major causes of World War I? Documents: [...]",
  "The major causes of World War I included the assassination of Archduke Franz Ferdinand, militarism, alliances, imperialism, and nationalism...",
  "gpt-4o",
  0.3,
  "llm"
);

// Conclude the trace
trace.conclude("The major causes of World War I included...");

// Flush the trace to Galileo
trace.flush();