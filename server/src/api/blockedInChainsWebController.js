import express from 'express';

// the web controller
const app = express();
app.use(express.json()); // Parse incoming JSON request bodies

// POST handler expecting an array of strings
app.post('/process-strings', (req, res) => {
  const data = req.body;

  // Validate that input is an array and contains only strings
  if (!Array.isArray(data) || !data.every(item => typeof item === 'string')) {
    return res.status(400).json({ 
      error: 'Invalid input: Payload must be an array of strings.' 
    });
  }

  // Example operation: Uppercase each string
  const result = data.map(str => str.toUpperCase());

  return res.status(200).json({
    message: 'Success',
    processed: result
  });
});

app.listen(3000, () => console.log('Server running on port 3000'));

// Testing the endpoint with cURL:
//curl -X POST http://localhost:3000/process-strings \
//  -H "Content-Type: application/json" \
 // -d '["apple", "banana", "cherry"]'