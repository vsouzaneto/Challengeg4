import test from 'node:test';import assert from 'node:assert/strict';
import {verifiedIdentity} from '../domain/auth_identity.mjs';
const uid='11111111-1111-4111-8111-111111111111',sid='22222222-2222-4222-8222-222222222222';
const jwt=p=>'header.'+Buffer.from(JSON.stringify(p)).toString('base64url')+'.signature';
test('Verified Auth result must match JWT subject; mutable metadata never sets role',()=>{const identity=verifiedIdentity(jwt({sub:uid,session_id:sid,exp:9999999999,user_metadata:{role:'administrator'}}),{id:uid,is_anonymous:false});assert.deepEqual(identity,{user_id:uid,auth_session_id:sid});assert.throws(()=>verifiedIdentity(jwt({sub:uid,session_id:sid,exp:9999999999}),{id:sid}));});
test('Anonymous, malformed, missing-session and expired tokens are rejected',()=>{const p={sub:uid,session_id:sid,exp:9999999999};assert.throws(()=>verifiedIdentity(jwt(p),{id:uid,is_anonymous:true}));assert.throws(()=>verifiedIdentity('bad',{id:uid}));assert.throws(()=>verifiedIdentity(jwt({...p,session_id:undefined}),{id:uid}));assert.throws(()=>verifiedIdentity(jwt({...p,exp:1}),{id:uid}));});
