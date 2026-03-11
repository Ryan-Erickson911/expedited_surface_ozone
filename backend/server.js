const express = require("express");
const multer = require("multer");
const axios = require("axios");

const upload = multer({ dest: "uploads/" });

const app = express();

app.post("/api/run-model", upload.single("shapefile"), async (req,res)=>{

const response = await axios.post(
"http://python-engine:8000/run-model",
{
pollutant: req.body.pollutant,
shapefile: req.file.path
}
);

res.json(response.data);

});

app.listen(3000);