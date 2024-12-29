// import the Genkit and Google AI plugin libraries
import { gemini15Flash, googleAI } from '@genkit-ai/googleai';
import { genkit, z } from 'genkit';
import { readFile, writeFile } from "fs/promises";
import { join } from "path";
import { exec } from 'child_process';
import util from 'node:util';
import { parallelLimit } from 'async';

const promiseExec = util.promisify(exec);

// configure a Genkit instance
//
const ai = genkit({
  // plugins: [googleAI({apiKey: "SOME_KEY_HERE"})],
  plugins: [googleAI()],
  model: gemini15Flash, // set default model
});

const systemPrompt = `You are a system to help identify the context and date from a jumble of text on the
back of pictures. You will be given multi line text input that may or may not have relevant date and
context information for the given picture. 
For Dates you should expect US date style so 03/20/95 for
March 20 1995, or March 83 which has no day so we will default to 03/01/1983. So to iterate for
dates if there is none default to 01/01/1980 for Janurary 1st 1980. If there is only a year default
to the given year and Janurary 1st. For example if you are given only "77" the date would be 01/01/77.
If there is not related date information default to 01/01/1980. If there seems to be multiple dates
defer to the earliest dates, for example if you get "1980,March 60" the earliest date is 03/01/1960.
If you get a date that looks like "Mar 911" remove this from all output and don't use it.
For context information this refers to all the rest of the text not related to the date, Just combine
this text to gether and remove any references to film products such as "Kodak", "FujiFilm" or other.
There also may be random asortment of other text like letters or numbers, if it doesn't seem like a
name or some context information drop it. If there is a double quotation mark (example: ") replace 
it with a single quote mark (example: ').`

const outputSchema = z.object({
  year: z.number().describe("The year of the picture in full number format. For example 2005 not 05. Expect integer value."),
  month: z.number().describe("The month of the picture date in number format. For example 2 not Feburary or Feb. Expect integer value. Also if no month identified default to 1. Max number is 12"),
  day: z.number().describe("The day from the date infromation. For example 15 in 03/15/1955. Expect integer value. Also if no day identified default to 1."),
  context: z.string().describe("The additional text context of the picture.")
});

async function Wrap(promise, context = "[Wrap]") {
  try {
    const result = await promise;
    return {ok: true, value: result};
  } catch (e) {
    return {ok: false, value: `${context} ${e}`, e};
  }
}

async function ExecCmd(command) {
  return Wrap(promiseExec(command), `Exec: "${command}"`);
}
// exiftool  -overwrite_original ./*.png

// -ImageDescription="Mom & Dad Wedding" -XMP-dc:Description="Mom & Dad Wedding"

// '-description<line1$/line2'

function CreateParam(param, text) {
  return `-${param}="${text.split("\n").join("&#xa;")}"`;
}

function PadDate(month) {
  return month.toString().padStart(2, '0');
}

function CreateTime(param, year, month, day) {
  return `-${param}="${year}:${PadDate(month)}:${PadDate(day)} 01:01:01"`
}

async function ExecuteExifOverwrite(outputFile, year, month, day, context) {
  let desc = "";
  if (context !== null && context !== "") {
    desc = ` -E ${CreateParam("ImageDescription", context)} ${CreateParam("XMP-dc:Description", context)}`;
  }
  let time = `${CreateTime("DateTimeOriginal", year, month, day)} ${CreateTime("EXIF:DateTimeOriginal", year, month, day)} ${CreateTime("XMP:CreateDate", year, month, day)} ${CreateTime("EXIF:CreateDate", year, month, day)} ${CreateTime("XMP:DateTimeOriginal", year, month, day)}`;
  // console.log("fullcommand", )
  return ExecCmd(`exiftool ${time}${desc} -overwrite_original ${outputFile}`);
}

async function ReadGenerateWriteExif(jsonFileName, cropFileName) {
  const readJson = await Wrap(readFile(jsonFileName), `Failed read "${jsonFileName}"`);
  if (!readJson.ok) {
    return readJson;
  }
  const parsedJson = await Wrap(Promise.resolve(JSON.parse(readJson.value)));
  if (!parsedJson.ok) {
    return parsedJson;
  }

  const visionApiJson = parsedJson.value;
  if (visionApiJson.length === 0) {
    // console.log(cropFileName, "No data");
    return {ok: true};
  }

  const fullText = visionApiJson[0].description;

  // make a generation request
  const prompt = `The jumble of text from the picture is: 
${fullText}`;
  const text = await ai.generate({ system: systemPrompt, prompt, output: {schema: outputSchema} });
  // console.log(text);
  // console.log(text.text);
  // console.log(text.output);
  if (text.output === null) {
    return {ok: false, value: `Invalid generated text from ${prompt}`};
  }
  const {context, day, month, year } = text.output;
  // console.log("output", context, day, month, year);
  
  const executionResult = await ExecuteExifOverwrite(cropFileName, year, month, day, context);
  if (!executionResult.ok) {
    return executionResult;
  }

  return {ok: true, value: {
    cmd: executionResult.value,
    cropFileName,
    prompt: fullText,
    context,
    day,
    month,
    year
  }};
}

(async() => {
  // The number of scans.
  // const n = 2;
  const n = 253;
  const pathToCropImgs = "/mnt/chromeos/MyFiles/LocalImageScans/OldPhotos/node_project/scan2_crop";
  const cropSuffix = "_front";
  const pathToJsons = "/mnt/chromeos/MyFiles/LocalImageScans/OldPhotos/node_project/scan2_jsons";
  const jsonSuffix = "_back.png";
  // console.log("fileJon", fileJson); 

  const failedNums = [];
  const funcs = [];
  for (let i = 0; i < n; i++) {
    funcs.push((async() => {
      const jsonFile = join(pathToJsons, `scan_${i}${jsonSuffix}.json`);
      const cropFile = join(pathToCropImgs, `scan_${i}${cropSuffix}.png`);
      const result = await ReadGenerateWriteExif(jsonFile, cropFile);
      if (!result.ok) {
        failedNums.push(i);
        console.error(`Error ${i}`);
        return result;
      } else {
        console.log(`Finished ${i}`);
      }
      return {ok: true, value: {...result.value, i} };
    }));
  }

  const results = await parallelLimit(funcs, 8);
  
  const outputData = [];
  for (const data of results) {
    if (!data.ok) {
      console.error(data.value);
      continue;
    }

    outputData.push({
      prompt: data.value.prompt,
      context: data.value.context,
      year: data.value.year,
      month: data.value.month,
      day: data.value.day,
      i: data.value.i
    });
  }
  // outputData = outputData.sort((a, b) => a.i - b.i);

  const jsonString = JSON.stringify(outputData, null, 2); // Pretty print with 2 spaces
  const writeResult = await Wrap(writeFile("./out.json", jsonString), `Failed write out json data`);
  if (!writeResult.ok) {
    console.error(writeResult.value, writeResult.e);
  }

  if (failedNums.length !== 0) {
    console.log("failedNums", failedNums.join(","))
  };
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

