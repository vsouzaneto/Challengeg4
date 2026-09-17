import {calculateROI} from './roi.ts';
const base={volume:1000,adoption:50,baseMinutes:10,proposedMinutes:4,hourlyCost:60,executions:500,executionCost:1,fixedCost:100,investment:2400,months:12};
const result=calculateROI(base);
if(result.hours!==50||result.net!==2400||result.payback!==1||result.roi!==275)throw Error('Cenário aritmético incorreto');
if(calculateROI({...base,executionCost:0,fixedCost:0,investment:0}).roi!==null)throw Error('Custo zero deve tornar ROI percentual indisponível');
if(calculateROI({...base,proposedMinutes:20}).hours>=0)throw Error('Esforço negativo não pode ser ocultado');
let rejected=false;try{calculateROI({...base,adoption:101})}catch{rejected=true}if(!rejected)throw Error('Adoção inválida não rejeitada');
console.log('ROI: cenário conhecido, custo zero, ganho negativo e validação aprovados.');
