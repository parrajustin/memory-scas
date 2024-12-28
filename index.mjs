// import the Genkit and Google AI plugin libraries
import { gemini15Flash, googleAI } from '@genkit-ai/googleai';
import { genkit, z } from 'genkit';

// configure a Genkit instance
//
const ai = genkit({
  // plugins: [googleAI({apiKey: "SOME_KEY_HERE"})],
  plugins: [googleAI()],
  model: gemini15Flash, // set default model
});

const getTime = ai.defineTool(
  {
    name: 'getTime',
    description: 'Get the formatted datetime string',
    inputSchema: z.object({ 
      year: z.string().describe('The year of the picture 1990 - 2024'),
      month: z.optional(z.string()).describe('The month of the picture, name or number if any provided'),
      day: z.optional(z.string()).describe('The day the of the month the picture was taken in number format'),
    }),
    outputSchema: z.string(),
  },
  async (input) => {
    if (input.year.length === 0) {
      return 'No valid date';
    }
    // Here, we would typically make an API call or database query. For this
    // example, we just return a fixed value.
    console.log("input", input);
    let fixedYear = input.year;
    if (fixedYear.length === 2) {
      const parsedYear = Number.parseInt(input.year);
      if (parsedYear <= 40) {
        fixedYear = `20${fixedYear}`;
      } else {
        fixedYear = `19${fixedYear}`;
      }
    }

    if (input.year && input.month === undefined) {
      return `Date is ${fixedYear}`;
    }
    if (input.year && input.month !== undefined && input.day !== undefined) {
      return `Date is `
    }
    return 'The current weather in ${input.location} is 63°F and sunny.';
  }
);

(async() => {
  // make a generation request
  const { text } = await ai.generate({ prompt: `Hello, your job is to identify the date and context text from a string. You should use the getTime tool passing in the year, month, and day if they are provided. Any text not related to date should be context text. The text I want you to identify is the following:    
7-15-97
Disney
JULY 97
JULY 97`, tools: [getTime]});
  console.log(text);
})();

// // Import the Fastify framework
// const fastify = require('fastify')({ logger: true });

// // Define a GET route
// fastify.get('/hello', async (request, reply) => {
//   return { message: 'Hello, World!' };
// });

// // Start the Fastify server
// const start = async () => {
//   try {
//     await fastify.listen({ port: 3000 });
//     console.log('Server is running on http://localhost:3000');
//   } catch (err) {
//     fastify.log.error(err);
//     process.exit(1);
//   }
// };

// start();





// const fs = require('fs');
// const path = require('path');
// const fastify = require('fastify')({ logger: true });

// // Define a GET route to read PNG images from a directory
// fastify.get('/images', async (request, reply) => {
//   const imagesDir = path.join(__dirname, 'images'); // Directory containing PNG images

//   try {
//     const files = fs.readdirSync(imagesDir);
//     const pngFiles = files.filter(file => path.extname(file).toLowerCase() === '.png');

//     return { images: pngFiles };
//   } catch (err) {
//     reply.status(500).send({ error: 'Unable to read directory', details: err.message });
//   }
// });

// // Start the Fastify server
// const start = async () => {
//   try {
//     await fastify.listen({ port: 3000 });
//     console.log('Server is running on http://localhost:3000');
//   } catch (err) {
//     fastify.log.error(err);
//     process.exit(1);
//   }
// };

// start();

