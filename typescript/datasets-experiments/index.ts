import "./config/env";  // side-effect: loads env vars
import { createDataset, getDataset, runExperiment, wrapOpenAI, createPromptTemplate } from "galileo";
import { MessageRole } from "galileo/dist/types/message.types";
import { OpenAI } from 'openai';

const projectName = "datasets-experiments";

async function runDatasetExperiment() {
  const openai = wrapOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }));


  const runner = async (input) => {
    const result = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ content: `Say hello ${input['name']}!`, role: 'user' }]
    });
    return [result.choices[0].message.content];
  };

  await runExperiment({
    name: 'Test Experiment',
    datasetName: 'roie-dataset',
    function: runner,
    metrics: ['instruction_adherence'],
    projectName
  });
}

// Run the experiment
runDatasetExperiment();

const dataset = await createDataset([
  {
    "input": "Which continent is Spain in?",
    "output": "Europe",
  },
  {
    "input": "Which continent is Japan in?",
    "output": "Asia",
  }]
, 'geography-dataset');

async function runPromptTemplateExperiment() {  

  const template = await createPromptTemplate({
    template: [
      { role: MessageRole.system, content: "You are a geography expert. Respond with only the continent name." },
      { role: MessageRole.user, content: "{{input}}" }
    ],
    projectName,
    name: "geography-prompt"
  });

  await runExperiment({
    name: "geography-experiment",
    datasetName: "geography-dataset", // Make sure you have a dataset created first
    promptTemplate: template,
    promptSettings: {
      max_tokens: 256,
      model_alias: "GPT-4o",
      temperature: 0.8
    },
    metrics: ["correctness"],
    projectName
  });
}

// Run the experiment
runPromptTemplateExperiment();