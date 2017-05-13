// Load our env variables
require('dotenv').config()

// Load packages
const fs = require('fs');
const http = require('http');
const https = require('https');
const express = require('express');
const privateKey  = fs.readFileSync('ssl/bluebook_solutions.key', 'utf8');
const certificate = fs.readFileSync('ssl/bluebook_solutions.crt', 'utf8');

// SSL credentials
const credentials = {
    key: privateKey,
    cert: certificate,
    passphrase: process.env.SSL_PASSPHRASE
};

// Simple static folder serving app
var app = express();
app.use(express.static('static'));

// HTTPS listener
https
  .createServer(credentials, app)
  .listen(process.env.HTTPS_PORT, () => {
    console.log(`HTTPS server listening on ${process.env.HTTPS_PORT}`);
  });

// Respond to http requests with HSTS redirection
http
  .createServer(function(req, res) {
    res.statusCode = 301;
    res.setHeader('Location', 'https://' + req.headers.host.split(':')[0] + req.url);
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    return res.end();
  })
  .listen(process.env.HTTP_PORT, () => {
    console.log(`HTTP -> HTTPS redicrection listening on port ${process.env.HTTP_PORT}`);
  });
