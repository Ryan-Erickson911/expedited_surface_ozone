require('dotenv').config();
import express, { json } from 'express';
import cors from 'cors';

import { ntlSummary } from './gee';
import { generateSummary } from './ai';

const app = express();
app.use(cors());
app.use(json());

// --- NTL endpoint ---
app.post('/ntlSummary', async (req, res) => {
    try {
        const stats = await ntlSummary(req.body);
        res.json(stats);
    } catch (err) {
        console.error(err);
        res.status(500).send("GEE error");
    }
});

// --- AI endpoint ---
app.post('/aiSummary', async (req, res) => {
    try {
        const summary = await generateSummary(req.body);
        res.send(summary);
    } catch (err) {
        console.error(err);
        res.status(500).send("AI error");
    }
});

app.listen(3000, () => console.log("Server running on port 3000"));