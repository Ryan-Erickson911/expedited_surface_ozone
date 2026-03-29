import express from "express";
import OpenAI from "openai";

const app = express();
app.use(express.json());

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

app.post("/api/ai-summary", async (req, res) => {
    const { cities, monitors } = req.body;

    const prompt = `
You are a GIS analyst. Summarize all objects in the selected location.

Cities inside area:
${cities.join(", ")}

EPA monitors inside area:
${monitors.map(m => `${m.site} in ${m.county} measured ${m.measurement}`).join("\n")}

Write geographic, ecological, and/or environmental summaries of this region.
`;

    const completion = await client.chat.completions.create({
        model: "gpt-4.1",
        messages: [{ role: "user", content: prompt }]
    });

    res.json({ summary: completion.choices[0].message.content });
});

app.listen(3000, () => console.log("Server running on 3000"));