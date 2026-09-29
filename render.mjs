import {chromium} from 'playwright';
import {mkdirSync,rmSync} from 'fs';
import {execSync} from 'child_process';
import path from 'path';
const [,, scene='scenes/circle-to-pill.html', out='out/test.mp4', dur='2', fps='60']=process.argv;
const N=Math.round(+dur*+fps), dir='out/frames';
rmSync(dir,{recursive:true,force:true});mkdirSync(dir,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'}), p=await b.newPage({viewport:{width:1280,height:720}});
await p.goto('file://'+path.resolve(scene));
for(let i=0;i<N;i++){await p.evaluate(t=>renderAt(t),i/+fps);
 await p.screenshot({path:`${dir}/f${String(i).padStart(4,'0')}.png`});}
await b.close();
execSync(`ffmpeg -y -loglevel error -framerate ${fps} -i ${dir}/f%04d.png -c:v libx264 -pix_fmt yuv420p -r ${fps} ${out}`);
console.log(N,'frames ->',out);
