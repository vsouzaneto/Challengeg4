// Build from canonical modules; isolate module locals and retain runtime npm imports.
import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import ts from '../web/frontend/node_modules/typescript/lib/typescript.js';
const root=new URL('../',import.meta.url);
async function moduleCode(file,exports){const s=await fs.readFile(new URL(file,root),'utf8');return `const {${exports.join(',')}}=(()=>{\n${s.replace(/^import .*;\n/gm,'').replaceAll('export function ','function ').replaceAll('export async function ','async function ').replaceAll('export const ','const ')}\nreturn {${exports.join(',')}};})();\n`;}
export async function bundle(kind){
 if(!['web','decisions','assistant','assistant-probe','users'].includes(kind))throw Error('Unknown Edge adapter.');
 let prefix=await moduleCode('web/domain/auth_identity.mjs',['verifiedIdentity'])+await moduleCode('web/edge/auth.ts',['authenticate']);
 if(kind==='web')prefix+=await moduleCode('web/domain/contracts.mjs',['contracts'])+await moduleCode('web/domain/import.mjs',['parseCsv','normalizeRows','auditSources','compareSources']);
 else if(kind==='decisions')prefix+=await moduleCode('web/domain/decision_scope.mjs',['normalizeScope','validateMetric']);
 else if(kind==='users')prefix+=await moduleCode('web/domain/permissions.mjs',['permissionCatalog','dependencies','expandPermissions','can','validateUserInput','validatePassword']);
 else prefix+=await moduleCode('web/domain/assistant.mjs',['assistantVersion','executeQuestion','publicError']);
 const entry=await fs.readFile(new URL(kind==='web'?'web/edge/index.ts':kind==='decisions'?'web/decisions/index.ts':kind==='users'?'web/users/index.ts':kind==='assistant-probe'?'web/assistant/probe.ts':'web/assistant/index.ts',root),'utf8');
 const input=prefix+entry.replace(/^import .* from ['"]\.[^\n]+\n/gm,'');
 const out=ts.transpileModule(input,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext},reportDiagnostics:true});
 if(out.diagnostics?.length)throw Error('TypeScript syntax diagnostics.');
 if(/from ['"]\./.test(out.outputText))throw Error('Unresolved relative import.');
 return out.outputText;
}
