// Loads the port env variable
require('dotenv').config()

var express = require('express');
var app = express();

app.use(express.static('static'));

app.listen(process.env.PORT, () => {
  console.log(`Static app listening on port ${process.env.PORT}!`)
});