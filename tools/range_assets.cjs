// Rebuild with: node tools/range_assets.cjs <path-to-war3-model>
// Dependency: war3-model 4.0.1 (MIT). Output assets are original geometry.
const fs = require('fs'), path = require('path');
const {parseMDL, generateMDX, parseMDX} = require(path.resolve(process.argv[2]));
const out = path.resolve(__dirname, '../assets/range');
fs.mkdirSync(out, {recursive:true});
function model(name, vertices, faces) {
  const extent = Math.ceil(Math.max(...vertices.flat().map(Math.abs))) + 4;
  const mdl = `Version { FormatVersion 800, }
Model "${name}" { NumGeosets 1, NumBones 1, BlendTime 0, MinimumExtent { -${extent}, -${extent}, -4 }, MaximumExtent { ${extent}, ${extent}, 4 }, BoundsRadius ${extent*2}, }
Sequences 1 { Anim "Stand" { Interval { 0, 1000 }, MinimumExtent { -${extent}, -${extent}, -4 }, MaximumExtent { ${extent}, ${extent}, 4 }, BoundsRadius ${extent*2}, } }
Textures 1 { Bitmap { Image "GSRI\\\\white.tga", } }
Materials 1 { Material { Layer { FilterMode Blend, Unshaded, TwoSided, Unfogged, NoDepthSet, static TextureID 0, static Alpha 1, } } }
Geoset {
Vertices ${vertices.length} { ${vertices.map(v=>'{ '+v.join(', ')+' },').join('\n')} }
Normals ${vertices.length} { ${vertices.map(()=>'{ 0, 0, 1 },').join('\n')} }
TVertices ${vertices.length} { ${vertices.map(()=>'{ 0.5, 0.5 },').join('\n')} }
VertexGroup { ${vertices.map(()=> '0,').join('\n')} }
Faces 1 ${faces.length} { Triangles { { ${faces.join(', ')} }, } }
Groups 1 1 { Matrices { 0 }, }
MinimumExtent { -${extent}, -${extent}, -4 }, MaximumExtent { ${extent}, ${extent}, 4 }, BoundsRadius ${extent*2},
Anim { MinimumExtent { -${extent}, -${extent}, -4 }, MaximumExtent { ${extent}, ${extent}, 4 }, BoundsRadius ${extent*2}, }
MaterialID 0, SelectionGroup 0, Unselectable,
}
Bone "Root" { ObjectId 0, GeosetId Multiple, GeosetAnimId None, }
PivotPoints 1 { { 0, 0, 0 }, }
`;
  fs.writeFileSync(path.join(out,name+'.mdl'),mdl);
  const parsedSource = parseMDL(mdl);
  parsedSource.Textures[0].Image = 'GSRI\\white.tga';
  const data = generateMDX(parsedSource);
  const parsed = parseMDX(data);
  if(parsed.Textures[0].Image !== 'GSRI\\white.tga') throw Error('texture path roundtrip');
  if(parsed.Geosets[0].Vertices.length !== vertices.length*3) throw Error('model roundtrip');
  fs.writeFileSync(path.join(out,name+'.mdx'),Buffer.from(data));
  console.log(name, vertices.length, 'vertices', faces.length/3, 'triangles');
}
const v=[], f=[];
for(let i=0;i<128;i++) {
  const a=i*2*Math.PI/128;
  for(const r of [99.7,100.3]) v.push([r*Math.cos(a),r*Math.sin(a),0]);
  const j=i*2, k=((i+1)%128)*2;
  f.push(j,k,j+1,j+1,k,k+1);
}
model('ring',v,f);
// Terrain renderer: each short segment gets its own position and slope.
model('terrain_line', [[-0.5,-3,0],[-0.5,3,0],[100.5,3,0],[100.5,-3,0]], [0,1,2,0,2,3]);
// One complete, world-sized capsule. Runtime only rotates/translates it.
const bv=[], bf=[];
function stroke(x1,y1,x2,y2,width=4) {
 const dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy);
 const nx=-dy/len*width/2,ny=dx/len*width/2,i=bv.length;
 bv.push([x1+nx,y1+ny,0],[x1-nx,y1-ny,0],[x2-nx,y2-ny,0],[x2+nx,y2+ny,0]);
 bf.push(i,i+1,i+2,i,i+2,i+3);
}
stroke(0,-120,1170,-120);stroke(0,120,1170,120);stroke(0,0,1170,0,2);
for(let j=0;j<32;j++) {
 const a=Math.PI/2+j*Math.PI/32,b=Math.PI/2+(j+1)*Math.PI/32;
 stroke(120*Math.cos(a),120*Math.sin(a),120*Math.cos(b),120*Math.sin(b));
 stroke(1170-120*Math.cos(a),-120*Math.sin(a),1170-120*Math.cos(b),-120*Math.sin(b));
}
model('ranger_path',bv,bf);
bv.length=0;bf.length=0;
// None Q: inherited level 1 radius 125; levels 2-4 override to 150.
// Display the nominal expanding corridor; native hit boundary needs game QA.
for (const radius of [125,150]) {
 bv.length=0;bf.length=0;
 stroke(0,-radius,825,-200);stroke(0,radius,825,200);
 stroke(0,-radius,0,radius);stroke(825,-200,825,200);stroke(0,0,825,0,2);
 model('none_fan_'+radius,bv,bf);
}
const tga=Buffer.alloc(18+4*4*4,255);tga.fill(0,0,18);tga[2]=2;tga.writeUInt16LE(4,12);tga.writeUInt16LE(4,14);tga[16]=32;tga[17]=0x28;
fs.writeFileSync(path.join(out,'white.tga'),tga);
