import OpenAI from 'openai';

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

async function generateSummary(data) {

    const prompt = `
You are a GIS analyst.

Summarize this selected region:

States: ${data.states.join(", ")}
Cities: ${data.cities.join(", ")}
EPA Monitors: ${data.monitors.join(", ")}

Nighttime Lights stats:
Mean: ${data.ntlStats.mean}
Min: ${data.ntlStats.min}
Max: ${data.ntlStats.max}
Sum: ${data.ntlStats.sum}

Explain what this implies about urbanization, monitoring coverage, and activity.
`;

    const res = await client.responses.create({
        model: "gpt-5-mini",
        input: prompt
    });

    return res.output_text;
}

export default { generateSummary };