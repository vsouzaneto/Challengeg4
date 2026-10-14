import fs from 'node:fs/promises';import path from 'node:path';import {bundle} from './edge_bundle.mjs';
const args=process.argv.slice(2);if(args.length!==2||args[0]!=='--output')throw Error('Usage: node scripts/build_decision_edge.mjs --output /path/index.js');
const output=path.resolve(args[1]);await fs.mkdir(path.dirname(output),{recursive:true});await fs.writeFile(output,await bundle('decisions'));process.stdout.write('Authenticated decision adapter packaged; no secrets included.\n');
