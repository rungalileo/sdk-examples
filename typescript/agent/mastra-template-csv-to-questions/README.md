# How to add Galileo to your Mastra project

[Example source here](https://github.com/mastra-ai/template-csv-to-questions).

## Step 1: Install OpenInference

To get started, install the OpenInference package in your project:

```bash
npm install @arizeai/openinference-mastra
```

## Step 2: Configure Galileo in your Mastra project

In your app definition you will need to add the following config:

```typescript
...
import {
  OpenInferenceOTLPTraceExporter,
  isOpenInferenceSpan,
} from "@arizeai/openinference-mastra";

export const mastra = new Mastra({
  ...,
  telemetry: {
    serviceName: "openinference-mastra-agent", // you can rename this to whatever you want to appear in the Phoenix UI
    enabled: true,
    sampling: {
      type: "always_on",
    },
    export: {
      type: "custom",
      exporter: new OpenInferenceOTLPTraceExporter({
        url: env.GALILEO_CONSOLE_URL,
        headers: {
          "Galileo-API-Key": env.GALILEO_API_KEY ?? "your-galileo-api-key",
          "Galileo-Project": env.GALILEO_PROJECT ?? "your-galileo-project",
          "Galileo-Log-Stream": env.GALILEO_LOG_STREAM ?? "default",
          "project": env.GALILEO_PROJECT ?? "your-galileo-project",
          "logstream": env.GALILEO_LOG_STREAM ?? "default",
        },
        spanFilter: isOpenInferenceSpan,
      }),
    },
  },
})
```

## Example CSV URLs

For testing, you can use these public CSV files:

- World GDP Data: `https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv`
- Cities Data: `https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv`
- Sample Dataset: `https://raw.githubusercontent.com/holtzy/data_to_viz/master/Example_dataset/1_OneNum.csv`
