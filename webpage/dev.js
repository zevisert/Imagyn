// Load our env variables
require('dotenv').config()

// Load packages
const https = require('https');
const express = require('express');

// Simple static folder serving app
var app = express();
app.use(express.static('static'));

app.listen(process.env.HTTP_PORT, () => {
  console.log(`Dev server listening on port ${process.env.HTTP_PORT}`);
});
