import { openai } from '@ai-sdk/openai';
import { Experimental_Agent as Agent, stepCountIs, tool } from 'ai';
import { z } from 'zod';
import { setupOtel } from './setupOtel';

setupOtel();

/**
 * The weather agent is a simple agent that can get the weather in a location and convert the temperature from Fahrenheit to Celsius using tools.
 */
const weatherAgent = new Agent({
  model: openai('gpt-4-turbo'),
  tools: {
    weather: tool({
      description: 'Get the weather in a location (in Fahrenheit)',
      inputSchema: z.object({
        location: z.string().describe('The location to get the weather for'),
      }),
      execute: async ({ location }) => ({
        location,
        temperature: 72,
      }),
    }),
    convertFahrenheitToCelsius: tool({
      description: 'Convert temperature from Fahrenheit to Celsius',
      inputSchema: z.object({
        temperature: z.number().describe('Temperature in Fahrenheit'),
      }),
      execute: async ({ temperature }) => {
        const celsius = Math.round((temperature - 32) * (5 / 9));
        return { celsius };
      },
    }),
  },
  stopWhen: stepCountIs(20),
  experimental_telemetry: { isEnabled: true }, // enable telemetry for the agent
  
});

const result = await weatherAgent.generate({
  prompt: 'What is the weather in San Francisco in celsius?',
});

console.log(result.text);