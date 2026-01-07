# CrewAI + Galileo Examples

This repo contains examples of how to use Galileo to instrument [CrewAI](https://www.crewai.com/) agents for observability and evaluation engineering.

## research_crew

The [resarch-crew](./research_crew/) is a quickstart tutorial. It is a completed version of the [CrewAI quickstart](https://docs.crewai.com/en/quickstart) and adds the
Galileo's [CrewAIEventListener](https://v2docs.galileo.ai/sdk-api/python/reference/handlers/crewai/handler),
an event handler implemented on top of OpenTelemetry (OTel). For more information, see
Galileo’s [Add Galileo to a CrewAI Application](https://v2docs.galileo.ai/how-to-guides/third-party-integrations/add-galileo-to-crewai/add-galileo-to-crewai)
how-to guide.

See the [README.md](./research_crew/README.md) for detailed setup instructions.
