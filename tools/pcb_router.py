"""Roteador de busca (A*) para a PCB do KiCad, em duas camadas (F.Cu e B.Cu). Grava no arquivo dado.

Le da propria PCB os pads, trilhas, vias e a zona HSE_GND_POUR das outras redes e a borda da placa, e acha um caminho
de 45 graus entre dois pads de uma rede, com via quando precisar. Grade de 0,05 mm, folga de 0,2 mm, trilha de 0,2 mm,
via de 0,6 / 0,3 mm. Nao mexe nas trilhas existentes. SO PARA USAR EM COPIA: depois rodar o DRC.
Limites: considera os pads pela caixa que os envolve; ignora larguras de classe (SDIO, USB, Power) e as regras do .kicad_dru;
e guloso (a ordem das redes importa); nao reenche zonas.

Uso como modulo (PY = Python do app do KiCad):
    from pcb_router import Router
    r = Router("COPIA.kicad_pcb"); r.route("GPS_TX", "U1", "37", "J6", "3"); r.b.Save("COPIA.kicad_pcb")
"""
import sys, math, heapq, json, pcbnew
mm=pcbnew.ToMM; M=pcbnew.FromMM
G=0.05
FC,BC=pcbnew.F_Cu,pcbnew.B_Cu
LAYS=(FC,BC)
class Router:
    def __init__(self,path):
        self.path=path; self.b=pcbnew.LoadBoard(path)
        bb=self.b.GetBoardEdgesBoundingBox()
        self.x0,self.y0,self.x1,self.y1=mm(bb.GetX()),mm(bb.GetY()),mm(bb.GetRight()),mm(bb.GetBottom())
        self.nx=int((self.x1-self.x0)/G)+3; self.ny=int((self.y1-self.y0)/G)+3
        self.ox=self.x0-G; self.oy=self.y0-G
    def idx(self,x,y): return int(round((x-self.ox)/G)),int(round((y-self.oy)/G))
    def xy(self,i,j): return self.ox+i*G,self.oy+j*G
    def build(self,net,w=0.2,clr=0.2,vr=0.3):
        hw=w/2; self.w=w; self.hw=hw
        nx,ny=self.nx,self.ny
        self.blk=[bytearray(nx*ny),bytearray(nx*ny)]   # centro da trilha
        self.vblk=bytearray(nx*ny)                       # centro de via
        tr,vi=clr+hw+0.02,clr+vr+0.02   # 0,02 mm de folga de seguranca contra arredondamento
        def mark(arr,cx0,cy0,cx1,cy1,fn,thr):
            i0,j0=self.idx(cx0-thr,cy0-thr); i1,j1=self.idx(cx1+thr,cy1+thr)
            i0-=8; j0-=8; i1+=8; j1+=8   # 0,4 mm de margem: cobre a meia-largura de trilhas largas
            for j in range(max(j0,0),min(j1,ny-1)+1):
                row=j*nx
                for i in range(max(i0,0),min(i1,nx-1)+1):
                    x,y=self.xy(i,j)
                    if fn(x,y)<thr: arr[row+i]=1
        def rectd(a,b_,c,d): 
            return lambda x,y: math.hypot(max(a-x,0,x-c),max(b_-y,0,y-d))
        def segd(x1,y1,x2,y2,hw_):
            dx,dy=x2-x1,y2-y1; L=dx*dx+dy*dy
            def f(x,y):
                t=0 if L==0 else max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L))
                return math.hypot(x-(x1+t*dx),y-(y1+t*dy))-hw_
            return f
        for fp in self.b.GetFootprints():
            for p in fp.Pads():
                if p.GetNetname()==net: continue
                r=p.GetBoundingBox(); a,b_,c,d=mm(r.GetX()),mm(r.GetY()),mm(r.GetRight()),mm(r.GetBottom())
                fn=rectd(a,b_,c,d)
                for k,ly in enumerate(LAYS):
                    if p.IsOnLayer(ly): mark(self.blk[k],a,b_,c,d,fn,tr)
                if p.IsOnLayer(FC) or p.IsOnLayer(BC): mark(self.vblk,a,b_,c,d,fn,vi)
        for t in self.b.GetTracks():
            if t.GetNetname()==net:
                if t.Type()==pcbnew.PCB_VIA_T:
                    x,y=mm(t.GetPosition().x),mm(t.GetPosition().y)
                    fn2=lambda xx,yy,x=x,y=y: math.hypot(xx-x,yy-y)-0.3
                    mark(self.vblk,x-0.3,y-0.3,x+0.3,y+0.3,fn2,0.5)
                continue
            if t.Type()==pcbnew.PCB_VIA_T:
                x,y=mm(t.GetPosition().x),mm(t.GetPosition().y); r=0.3
                fn=lambda xx,yy,x=x,y=y,r=r: math.hypot(xx-x,yy-y)-r
                for k in (0,1): mark(self.blk[k],x-r,y-r,x+r,y+r,fn,tr)
                mark(self.vblk,x-r,y-r,x+r,y+r,fn,vi)
                # via com via: centros a pelo menos 0,8
                fn2=lambda xx,yy,x=x,y=y: math.hypot(xx-x,yy-y)-0.3
                mark(self.vblk,x-0.3,y-0.3,x+0.3,y+0.3,fn2,0.5)
            else:
                k=0 if t.GetLayer()==FC else 1
                x1,y1,x2,y2=mm(t.GetStart().x),mm(t.GetStart().y),mm(t.GetEnd().x),mm(t.GetEnd().y); h=mm(t.GetWidth())/2
                fn=segd(x1,y1,x2,y2,h)
                mark(self.blk[k],min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2),fn,tr)
                mark(self.vblk,min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2),fn,vi)
        for z in self.b.Zones():
            if z.GetZoneName()=="HSE_GND_POUR" and net!="GND":
                r=z.GetBoundingBox(); a,b_,c,d=mm(r.GetX()),mm(r.GetY()),mm(r.GetRight()),mm(r.GetBottom())
                fn=rectd(a,b_,c,d); mark(self.blk[0],a,b_,c,d,fn,0.5+hw); mark(self.vblk,a,b_,c,d,fn,0.5+vr)
        # borda da placa
        m=0.7
        for j in range(ny):
            for i in range(nx):
                x,y=self.xy(i,j)
                if not (self.x0+m<x<self.x1-m and self.y0+m<y<self.y1-m):
                    self.blk[0][j*nx+i]=1; self.blk[1][j*nx+i]=1; self.vblk[j*nx+i]=1
    def pad_nodes(self,pad,layer):
        r=pad.GetBoundingBox(); a,b_,c,d=mm(r.GetX()),mm(r.GetY()),mm(r.GetRight()),mm(r.GetBottom())
        i0,j0=self.idx(a,b_); i1,j1=self.idx(c,d); k=0 if layer==FC else 1
        return {(i,j,k) for i in range(i0,i1+1) for j in range(j0,j1+1) if a-1e-6<=self.xy(i,j)[0]<=c+1e-6 and b_-1e-6<=self.xy(i,j)[1]<=d+1e-6}
    def astar(self,starts,goals,vcost=8.0,turn=0.15,window=None):
        nx=self.nx; blk=self.blk; vb=self.vblk
        dirs=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        goal_xy=[self.xy(i,j) for (i,j,k) in list(goals)[:1]]
        gx,gy=goal_xy[0]
        def h(i,j):
            x,y=self.xy(i,j); return math.hypot(x-gx,y-gy)
        pq=[]; best={}; prev={}; cnt=[0]
        for s in starts:
            best[(s,None)]=0; cnt[0]+=1; heapq.heappush(pq,(h(s[0],s[1]),0,cnt[0],s,None))
        n=0
        while pq:
            f,g,_c,s,d=heapq.heappop(pq)
            if best.get((s,d),1e18)<g-1e-9: continue
            if s in goals:
                path=[s]; key=(s,d)
                while key in prev: key=prev[key]; path.append(key[0])
                return path[::-1]
            n+=1
            if n>2500000: return None
            i,j,k=s
            for di,dj in dirs:
                ni,nj=i+di,j+dj
                if not(0<=ni<self.nx and 0<=nj<self.ny): continue
                if blk[k][nj*nx+ni] and (ni,nj,k) not in goals and s not in starts: continue
                if blk[k][nj*nx+ni] and (ni,nj,k) not in goals: continue
                c=math.hypot(di,dj)*G*1.0+( turn if d not in (None,(di,dj)) else 0)
                ns=(ni,nj,k); key=(ns,(di,dj)); ng=g+c
                if ng<best.get(key,1e18):
                    best[key]=ng; prev[key]=(s,d); cnt[0]+=1; heapq.heappush(pq,(ng+h(ni,nj),ng,cnt[0],ns,(di,dj)))
            if not vb[j*nx+i]:
                nk=1-k; ns=(i,j,nk); key=(ns,None); ng=g+vcost
                if not blk[nk][j*nx+i] or ns in goals:
                    if ng<best.get(key,1e18):
                        best[key]=ng; prev[key]=(s,d); cnt[0]+=1; heapq.heappush(pq,(ng+h(i,j),ng,cnt[0],ns,None))
        return None
    def to_items(self,path,p0,p1,net,layer0,layer1):
        """polilinha por camada e vias a partir do caminho de nos"""
        segs=[]; vias=[]
        cur=[self.xy(path[0][0],path[0][1])]; curk=path[0][2]
        for a,b_ in zip(path[:-1],path[1:]):
            if a[2]!=b_[2]:
                segs.append((curk,cur)); vias.append(self.xy(a[0],a[1])); cur=[self.xy(b_[0],b_[1])]; curk=b_[2]
            else: cur.append(self.xy(b_[0],b_[1]))
        segs.append((curk,cur))
        # junta pad inicial e final
        k0=segs[0][0]; segs[0][1].insert(0,p0)
        segs[-1][1].append(p1)
        out=[]
        for k,pts in segs:
            # remove colineares
            s=[pts[0]]
            for q in pts[1:]:
                if q==s[-1]: continue
                if len(s)>=2:
                    ax,ay=s[-2]; bx,by=s[-1]
                    if abs((bx-ax)*(q[1]-by)-(by-ay)*(q[0]-bx))<1e-9: s[-1]=q; continue
                s.append(q)
            out.append((k,s))
        return out,vias
    def add(self,net,items,vias,w=0.2):
        n=self.b.FindNet(net)
        for k,pts in items:
            for (x1,y1),(x2,y2) in zip(pts[:-1],pts[1:]):
                t=pcbnew.PCB_TRACK(self.b); t.SetStart(pcbnew.VECTOR2I(M(x1),M(y1))); t.SetEnd(pcbnew.VECTOR2I(M(x2),M(y2)))
                t.SetWidth(M(w)); t.SetLayer(LAYS[k]); t.SetNet(n); self.b.Add(t)
        for x,y in vias:
            v=pcbnew.PCB_VIA(self.b); v.SetPosition(pcbnew.VECTOR2I(M(x),M(y))); v.SetViaType(pcbnew.VIATYPE_THROUGH)
            try: v.SetWidth(pcbnew.F_Cu,M(0.6))
            except TypeError: v.SetWidth(M(0.6))
            v.SetDrill(M(0.3)); v.SetLayerPair(FC,BC); v.SetNet(n); self.b.Add(v)
    def route(self,net,ref0,num0,ref1,num1,w=0.2):
        self.build(net,w)
        p0=[q for q in self.b.FindFootprintByReference(ref0).Pads() if q.GetNumber()==num0][0]
        p1=[q for q in self.b.FindFootprintByReference(ref1).Pads() if q.GetNumber()==num1][0]
        l0=FC if p0.IsOnLayer(FC) else BC; l1=FC if p1.IsOnLayer(FC) else BC
        s=self.pad_nodes(p0,l0); g=self.pad_nodes(p1,l1)
        path=self.astar(s,g)
        if path is None: print("SEM CAMINHO:",net,ref0,num0,"->",ref1,num1); return False
        c0=(mm(p0.GetPosition().x),mm(p0.GetPosition().y)); c1=(mm(p1.GetPosition().x),mm(p1.GetPosition().y))
        items,vias=self.to_items(path,c0,c1,net,l0,l1)
        L=sum(math.dist(a,b_) for k,pts in items for a,b_ in zip(pts[:-1],pts[1:]))
        print("%s %s.%s -> %s.%s: %.1f mm, %d vias, camadas %s"%(net,ref0,num0,ref1,num1,L,len(vias),[("F" if k==0 else "B",len(pts)) for k,pts in items]))
        self.add(net,items,vias,w); return True
