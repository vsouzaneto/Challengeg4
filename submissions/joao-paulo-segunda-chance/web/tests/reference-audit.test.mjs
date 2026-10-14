import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {parseCsv,auditSources} from '../domain/import.mjs';
const dir=process.env.CHALLENGE_DATA_DIR;
test('89 resultados da auditoria web coincidem com o auditor independente Python', {skip:!dir},()=>{
 const names={accounts:'accounts',subscriptions:'subscriptions',usage:'feature_usage',support:'support_tickets',churn:'churn_events'};
 const d={};for(const [key,name]of Object.entries(names)){const {headers,rows}=parseCsv(fs.readFileSync(`${dir}/ravenstack_${name}.csv`,'utf8'));d[key]=rows.map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]])));}
 const web=auditSources(d),python=JSON.parse(fs.readFileSync(process.env.CHALLENGE_AUDIT_REPORT,'utf8'));
 assert.equal(web.findings.length,python.findings.length);for(const x of python.findings){const y=web.findings.find(r=>r.code===x.code);assert.ok(y,x.code);assert.equal(y.count,x.count,x.code);assert.equal(y.denominator,x.denominator,x.code);}
});
