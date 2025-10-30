// Using the Docker API
const FormData = require('form-data');
const fs = require('fs');

const analyzeSong = async (filepath) => {
  const form = new FormData();
  form.append('file', fs.createReadStream(filepath));

  const response = await fetch('http://localhost:8000/analyze', {
    method: 'POST',
    body: form
  });

  return await response.json();
};

const result = await analyzeSong('song.mp3');
console.log(result.mood);