import dotenv from "dotenv";
import { GalileoScorers, runExperiment } from "galileo";

import { getUsersHoroscope } from "./app.ts";

// Load environment variables from .env
dotenv.config();

(async () => {
    // Run an experiment to evaluate horoscope retrieval

    const dataset = [{ input: "Aquarius" }, { input: "Taurus" }, { input: "Gemini" }, { input: "Leo" }];

    const experiment = await runExperiment({
        name: "horoscope-experiment",
        dataset,
        function: async (row: { value: string }) => {
            return await getUsersHoroscope(row.value)
        },
        metrics: [
            GalileoScorers.ToolErrorRate,
            GalileoScorers.ToolSelectionQuality,
            GalileoScorers.ChunkAttributionUtilization,
            GalileoScorers.ContextAdherence,
        ],
        projectName: process.env.GALILEO_PROJECT,
    });

    console.log("Experiment Results:");
    console.log(experiment.link);
})();