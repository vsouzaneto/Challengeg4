// Authorization is persisted and checked in Postgres. These rules also drive the editor.
export const permissionCatalog = [
 {code:'analytics.read',label:'Visão executiva e diagnóstico',group:'Consulta'},
 {code:'accounts.read',label:'Contas e detalhes',group:'Consulta'},
 {code:'quality.read',label:'Dados e qualidade',group:'Consulta'},
 {code:'method.read',label:'Metodologia',group:'Consulta'},
 {code:'decisions.read',label:'Consultar decisões e evidências',group:'Decisões'},
 {code:'decisions.create',label:'Registrar decisões',group:'Decisões'},
 {code:'actions.update',label:'Atualizar e concluir ações',group:'Decisões'},
 {code:'data.import',label:'Importar e preparar prévia',group:'Atualização'},
 {code:'data.publish',label:'Publicar atualização',group:'Atualização'},
 {code:'assistant.use',label:'Assistente IA e histórico próprio',group:'Assistente'}
];
export const dependencies={
 'decisions.read':['analytics.read','accounts.read','quality.read'],
 'decisions.create':['decisions.read'],'actions.update':['decisions.read'],
 'data.import':['quality.read','accounts.read','analytics.read'],'data.publish':['data.import'],
 'assistant.use':['analytics.read','accounts.read','quality.read']
};
export function expandPermissions(codes){const out=new Set(codes);for(const p of out)for(const d of dependencies[p]??[])out.add(d);return [...out].sort();}
export function can(user,permission){return !user?.password_change_required&&(['administrator','super_admin'].includes(user?.role)||(user?.permissions??[]).includes(permission));}
export function validateUserInput(body,creating=false){
 if(!body||typeof body!=='object'||Array.isArray(body))throw Error('Dados inválidos.');
 const name=String(body.name??'').trim(),email=String(body.email??'').trim().toLowerCase();
 if(name.length<2||name.length>100)throw Error('Nome deve ter entre 2 e 100 caracteres.');
 if(creating&&(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)||email.length>254))throw Error('Informe um e-mail válido.');
 if(!['administrator','user'].includes(body.role))throw Error('Perfil inválido.');
 const codes=body.permissions;
 if(!Array.isArray(codes)||codes.some(x=>typeof x!=='string'||!permissionCatalog.some(p=>p.code===x)))throw Error('Permissões inválidas.');
 const permissions=body.role==='administrator'?[]:expandPermissions(codes);
 if(body.role==='user'&&!permissions.length)throw Error('Selecione ao menos uma permissão.');
 if(!creating&&typeof body.active!=='boolean')throw Error('Situação inválida.');
 return {name,email,role:body.role,permissions,active:creating?true:body.active};
}
export function validatePassword(password){if(typeof password!=='string'||password.length<12||password.length>128||!/[a-z]/.test(password)||!/[A-Z]/.test(password)||!/[0-9]/.test(password))throw Error('Use de 12 a 128 caracteres, com maiúscula, minúscula e número.');return password;}
