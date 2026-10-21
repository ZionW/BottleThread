import Rhino, math
G=Rhino.Geometry

def build_profile(q,s,tol):
    root=q['E']/2-.02;crest=q['T']/2;depth=crest-root
    half=q['c']/2;lo=half+depth*math.tan(math.radians(q['bottom']));hi=half+depth*math.tan(math.radians(q['top']))
    coords=[(root-.4,-lo-q['ext']),(root,-lo-q['ext']),(root,-lo),(crest,-half),(crest,half),(root,hi),(root,hi+q['ext']),(root-.4,hi+q['ext'])]
    radii=[0,0,q['Rroot'],q['Rcrest'],q['Rcrest'],q['Rroot'],0,0]
    vs=[G.Point3d(x*s,0,z*s) for x,z in coords];start=[];end=[];arcs=[]
    for i,v in enumerate(vs):
     rr=radii[i]*s
     if not rr:start.append(v);end.append(v);arcs.append(None);continue
     u=vs[(i-1)%8]-v;w=vs[(i+1)%8]-v;lu=u.Length;lw=w.Length;u.Unitize();w.Unitize()
     angle=math.acos(max(-1,min(1,G.Vector3d.Multiply(u,w))));d=rr/math.tan(angle/2)
     if d>=min(lu,lw):raise Exception(q['name']+' radius does not fit vertex '+str(i))
     a=v+u*d;b=v+w*d;bis=u+w;bis.Unitize();center=v+bis*(rr/math.sin(angle/2));rad=v-center;rad.Unitize()
     arc=G.Arc(a,center+rad*rr,b)
     start.append(a);end.append(b);arcs.append(arc)
    pc=G.PolyCurve()
    for i in range(8):
     if arcs[i] is not None:pc.Append(arcs[i])
     if end[i].DistanceTo(start[(i+1)%8])>tol:pc.Append(G.LineCurve(end[i],start[(i+1)%8]))
    return pc


def generate(doc,q):
    s=Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Millimeters,doc.ModelUnitSystem);tol=.001*s

    if not all(math.isfinite(float(q[k])) for k in ['T','E','I_test','H','pitch','top','bottom','c','Rcrest','Rroot','full_degrees','S','runin','runout']): raise ValueError('參數必須是有限數值')
    if not 0<q['I_test']<q['E']<q['T']: raise ValueError('尺寸必須符合 0 < I < E < T')
    if not .1<=q['pitch']<=100 or not .1<=q['H']<=1000: raise ValueError('螺距或高度超出範圍')
    if not 0<=q['top']<80 or not 0<=q['bottom']<80: raise ValueError('牙側角度需介於 0 與 80 度')
    if min(q['Rcrest'],q['Rroot'])<0 or q['c']<=0: raise ValueError('圓角不可為負，牙頂寬需大於零')
    if not 30<=q['full_degrees']<=1440: raise ValueError('有效螺紋角度需介於 30 與 1440 度')
    if min(q['runin'],q['runout'])<5 or max(q['runin'],q['runout'])>360: raise ValueError('漸入／收頭角度需介於 5 與 360 度')
    if q['S']<0: raise ValueError('起牙距離不可為負')
    q=dict(q)
    q['ext']=max(.05,q['Rroot']*max(math.tan(math.radians((90-q['top'])/2)),math.tan(math.radians((90-q['bottom'])/2)))+.03)
    depth=(q['T']-q['E'])/2+.02
    halfspan=q['c']/2+depth*max(math.tan(math.radians(q['top'])),math.tan(math.radians(q['bottom'])))+q['ext']
    if q['H']-q['S']-q['c']/2-(q['full_degrees']+q['runin']+q['runout'])*q['pitch']/360-halfspan<=0: raise ValueError('瓶口高度不足，請增加高度或減少螺紋圈數')
    def cy(r,h):return G.Cylinder(G.Circle(G.Plane.WorldXY,r*s),h*s).ToBrep(True,True)
    mode=q.get('output','neck')
    if mode not in ['neck','cap']: raise ValueError('未知生成類型')
    radial=q.get('radial_gap',.2);axial=q.get('axial_gap',.05);wall=q.get('cap_wall',1.5);topwall=q.get('cap_top',1.5);headgap=q.get('head_gap',.4)
    if mode=='cap':
     if not all(math.isfinite(float(v)) for v in [radial,axial,wall,topwall,headgap]) or min(radial,axial,headgap)<0 or min(wall,topwall)<.3: raise ValueError('間隙不可為負，蓋壁與頂厚至少 0.3 mm')
    pq=dict(q)
    if mode=='cap':pq.update(T=q['T']+2*radial,E=q['E']+2*radial,c=q['c']+2*axial)
    profile=build_profile(pq,s,tol);segments=profile.DuplicateSegments();rows=[]
    runin=q.get('runin',30);runout=q.get('runout',30)
    total=q['full_degrees']+runin+runout
    start=-360 if mode=='cap' else 0
    stop=total+360 if mode=='cap' else total
    count=max(12,int((stop-start)/5))
    for i in range(count+1):
     theta=start+(stop-start)*i/count;t=max(0,min(1,min(theta/max(runin,0.001),(total-theta)/max(runout,0.001))));fade=t*t*(3-2*t)
     shift=0 if mode=='cap' else (q['T']/2-q['E']/2+.12)*(1-fade)
     z=q['H']-q['S']-q['c']/2-theta*q['pitch']/360
     row=[]
     for seg in segments:
      c=seg.DuplicateCurve();c.Transform(G.Transform.Translation(-shift*s,0,z*s));c.Transform(G.Transform.Rotation(math.radians((-1 if q.get('right_hand',True) else 1)*theta),G.Vector3d.ZAxis,G.Point3d.Origin));row.append(c)
     rows.append(row)
    faces=[]
    for j in range(len(segments)):faces.extend(G.Brep.CreateFromLoft([row[j] for row in rows],G.Point3d.Unset,G.Point3d.Unset,G.LoftType.Normal,False))
    joined=G.Brep.JoinBreps(faces,tol)
    if not joined or len(joined)!=1:raise Exception(q['name']+' loft join failed')
    rib=joined[0].CapPlanarHoles(tol)
    if not rib.IsValid or not rib.IsSolid:raise Exception(q['name']+' invalid rib')
    if rib.SolidOrientation==G.BrepSolidOrientation.Inward:rib.Flip()
    if mode=='cap':
     def cylinder_at(r,z,h):
      b=cy(r,h);b.Transform(G.Transform.Translation(0,0,z*s));return b
     def one(items,label):
      if not items or len(items)!=1 or not items[0].IsValid or not items[0].IsSolid:raise ValueError(label+' 無法生成封閉實體')
      return items[0]
     ceiling=q['H']+axial+headgap
     bottom=max(0,q['H']-q['S']-q['c']/2-total*q['pitch']/360-halfspan-1)
     outer=q['T']/2+radial+wall;inner=q['E']/2+radial
     shell=one(G.Brep.CreateBooleanDifference(cylinder_at(outer,bottom,ceiling+topwall-bottom),cylinder_at(inner,bottom-1,ceiling-bottom+1),tol),'瓶蓋外殼')
     clip=cylinder_at(outer+1,bottom-1,ceiling-bottom+.9)
     cutter=one(G.Brep.CreateBooleanIntersection(rib,clip,tol),'母牙切削體')
     cap=one(G.Brep.CreateBooleanDifference(shell,cutter,tol),'母牙瓶蓋')
     independent=(q.get('cap_thread_model')=='independent_inward_rib' or q.get('id')=='pco1881')
     if independent:
      d=float(q.get('cap_thread_depth',.9));cw=float(q.get('cap_thread_width',.5));fade_angle=float(q.get('cap_thread_run',30))
      if not all(math.isfinite(v) for v in [d,cw,fade_angle]) or not .2<=d<=1.2 or not .2<=cw<=1 or not 10<=fade_angle<=90:raise ValueError('瓶蓋牙高 0.2–1.2、牙寬 0.2–1.0 mm、收頭 10–90°')
      base=q['T']/2+radial
      if base-d<=q['E']/2+radial:raise ValueError('瓶蓋牙高超出瓶口配合空間')
      cp=dict(q,E=.04,T=2*(d+.02),c=cw,top=q['bottom'],bottom=q['top'],Rcrest=.1,Rroot=.1,ext=.15)
      inward=build_profile(cp,s,tol)
      inward.Transform(G.Transform.Mirror(G.Plane(G.Point3d.Origin,G.Vector3d.XAxis)))
      inward.Transform(G.Transform.Translation((base+.02)*s,0,0))
      segs=inward.DuplicateSegments();rr=[]
      for i in range(max(12,int(total/5))+1):
       theta=total*i/max(12,int(total/5));t=max(0,min(1,theta/fade_angle,(total-theta)/fade_angle));fade=t*t*(3-2*t)
       z=q['H']-q['S']-q['c']/2-q['pitch']/2-theta*q['pitch']/360
       row=[]
       for seg in segs:
        cc=seg.DuplicateCurve();cc.Transform(G.Transform.Translation((d+.12)*(1-fade)*s,0,z*s));cc.Transform(G.Transform.Rotation(math.radians((-1 if q.get('right_hand',True) else 1)*theta),G.Vector3d.ZAxis,G.Point3d.Origin));row.append(cc)
       rr.append(row)
      ff=[]
      for j in range(len(segs)):ff.extend(G.Brep.CreateFromLoft([row[j] for row in rr],G.Point3d.Unset,G.Point3d.Unset,G.LoftType.Normal,False))
      joined=G.Brep.JoinBreps(ff,tol)
      if not joined or len(joined)!=1:raise ValueError('瓶蓋凸牙接合失敗')
      tooth=joined[0].CapPlanarHoles(tol)
      if tooth.SolidOrientation==G.BrepSolidOrientation.Inward:tooth.Flip()
      shell=one(G.Brep.CreateBooleanDifference(cylinder_at(outer,bottom,ceiling+topwall-bottom),cylinder_at(base,bottom-1,ceiling-bottom+1),tol),'凸牙瓶蓋外殼')
      combined=one(G.Brep.CreateBooleanUnion([shell,tooth],tol),'獨立凸牙')
      # The expanded male sweep is a clearance mask, not the source of the female tooth.
      cap=one(G.Brep.CreateBooleanDifference(combined,cutter,tol),'凸牙配合間隙')
     removed=(abs(G.VolumeMassProperties.Compute(shell).Volume)-abs(G.VolumeMassProperties.Compute(cap).Volume))/s**3
     if not independent and removed<.01:raise ValueError('母牙凹槽未生成')
     capvents={'enabled':False,'count':0,'removed_volume_mm3':0}
     if q.get('cap_vents',q.get('vents',False)):
      width=float(q.get('vent_width',1.82));phase=float(q.get('vent_phase',0));angles=q.get('vent_angles',[-28,28,152,208])
      if not math.isfinite(width) or not .3<=width<=4 or not math.isfinite(phase) or len(angles)!=4:raise ValueError('瓶蓋排氣參數無效')
      # Cut only inward thread material; preserve the cylindrical cap wall and lid.
      base=q['T']/2+radial;cuts=[]
      for angle in angles:
       box=G.BoundingBox(G.Point3d(0,-width*s/2,(bottom-.1)*s),G.Point3d((base-.01)*s,width*s/2,(ceiling-.01)*s)).ToBrep()
       box.Transform(G.Transform.Rotation(math.radians(-angle-phase),G.Vector3d.ZAxis,G.Point3d.Origin))
       slot=one(G.Brep.CreateBooleanIntersection(box,cylinder_at(base-.01,bottom-1,ceiling-bottom+2),tol),'瓶蓋缺口徑向限制')
       cut=one(G.Brep.CreateBooleanDifference(cap,slot,tol),'瓶蓋排氣缺口')
       delta=(abs(G.VolumeMassProperties.Compute(cap).Volume)-abs(G.VolumeMassProperties.Compute(cut).Volume))/s**3
       if delta<.001:raise ValueError('瓶蓋排氣缺口未切到內牙')
       cuts.append(delta);cap=cut
      capvents={'enabled':True,'count':4,'width_mm':width,'angles_clockwise_from_thread_start_deg':[a+phase for a in angles],'per_cut_volume_mm3':cuts,'removed_volume_mm3':sum(cuts),'root_land_mm':.01,'shape':'rectangular approximation; cap wall and lid retained'}
     report={'specification':q,'output':'cap','valid':cap.IsValid,'solid':cap.IsSolid,'naked_edges':sum(1 for e in cap.Edges if int(e.Valence)==1),'measured_major_diameter_mm':2*outer,'cap_outer_diameter_mm':2*outer,'cap_height_mm':ceiling+topwall-bottom,'groove_removed_volume_mm3':removed,'radial_gap_mm':radial,'axial_gap_each_side_mm':axial,'minimum_wall_mm':wall,'top_thickness_mm':topwall,'seal_validation':'not performed','vents':capvents}
     if independent:report.update(thread_construction='independent_inward_rib',cap_thread_depth_mm=d,cap_thread_width_mm=cw,cap_thread_run_degrees=fade_angle,tooth_added_volume_mm3=-removed-capvents['removed_volume_mm3'],cap_thread_standard_status='adjustable reference, not certified closure drawing');report.pop('groove_removed_volume_mm3',None)
     if report['naked_edges']:raise ValueError('瓶蓋存在裸邊')
     return cap,report
    bore=cy(q['I_test']/2,q['H']+2);bore.Transform(G.Transform.Translation(0,0,-s))
    # Cut the bore last: faded thread roots can extend through a thin neck wall.
    union=G.Brep.CreateBooleanUnion([cy(q['E']/2,q['H']),rib],tol)
    if not union or len(union)!=1 or not union[0].IsValid or not union[0].IsSolid:raise Exception(q['name']+' union failed')
    hollow=G.Brep.CreateBooleanDifference(union[0],bore,tol)
    if not hollow or len(hollow)!=1 or not hollow[0].IsValid or not hollow[0].IsSolid:raise ValueError('瓶口內孔切削失敗')
    neck=hollow[0]
    if abs(neck.GetBoundingBox(True).Max.X/s-q['T']/2)>.01:raise Exception(q['name']+' missing thread crest')
    vent_report={'enabled':False,'count':0,'removed_volume_mm3':0}
    if q.get('vents',False):
     width=float(q.get('vent_width',1.82));phase=float(q.get('vent_phase',0))
     angles=q.get('vent_angles',[-28,28,152,208])
     if not math.isfinite(width) or not .3<=width<=4 or not math.isfinite(phase):raise ValueError('排氣缺口寬度需為 0.3–4 mm，角位需為有限數值')
     if len(angles)!=4:raise ValueError('此版 PCO 排氣缺口需為四處')
     before=abs(G.VolumeMassProperties.Compute(neck).Volume)/s**3
     zlo=max(0,q['H']-q['S']-q['c']/2-total*q['pitch']/360-halfspan-.1)
     zhi=min(q['H']-.1,q['H']-q['S']-q['c']/2+halfspan+.1)
     cuts=[]
     for angle in angles:
      box=G.BoundingBox(G.Point3d((q['E']/2+.01)*s,-width*s/2,zlo*s),G.Point3d((q['T']/2+1)*s,width*s/2,zhi*s)).ToBrep()
      box.Transform(G.Transform.Rotation(math.radians(-angle-phase),G.Vector3d.ZAxis,G.Point3d.Origin))
      cut=G.Brep.CreateBooleanDifference(neck,box,tol)
      if not cut or len(cut)!=1 or not cut[0].IsValid or not cut[0].IsSolid:raise ValueError('排氣缺口接合失敗')
      delta=(abs(G.VolumeMassProperties.Compute(neck).Volume)-abs(G.VolumeMassProperties.Compute(cut[0]).Volume))/s**3
      if delta<.001:raise ValueError('排氣缺口未切到螺紋')
      cuts.append(delta);neck=cut[0]
     vent_report={'enabled':True,'count':4,'width_mm':width,'angles_clockwise_from_thread_start_deg':[a+phase for a in angles],'removed_volume_mm3':before-abs(G.VolumeMassProperties.Compute(neck).Volume)/s**3,'per_cut_volume_mm3':cuts,'root_land_mm':.01,'shape':'rectangular approximation; vent-end radius not modeled'}
    ok,curves,points=G.Intersect.Intersection.BrepPlane(neck,G.Plane(G.Point3d.Origin,G.Vector3d.YAxis),.0001*s)
    angles=[];radii=[]
    for curve in curves or []:
     for seg in curve.DuplicateSegments():
      for i in range(1,21):
       t=seg.Domain.ParameterAt(i/21.0);p=seg.PointAt(t)
       if q['E']/2+.005<p.X/s<q['T']/2+.001 and 1<p.Z/s<q['H']-1:
        k=seg.CurvatureAt(t).Length*s;v=seg.TangentAt(t);a=math.degrees(math.atan2(abs(v.Z),abs(v.X)))
        if k<.005 and 1<a<89:angles.append(round(a,3))
        if k>1 and any(abs(1/k-r)<.002 for r in [q['Rcrest'],q['Rroot']]):radii.append(round(1/k,3))
    report={'specification':q,'valid':neck.IsValid,'solid':neck.IsSolid,'naked_edges':sum(1 for e in neck.Edges if int(e.Valence)==1),'measured_flank_angles_deg':sorted(set(angles)),'measured_profile_radii_mm':sorted(set(radii)),'measured_major_diameter_mm':2*neck.GetBoundingBox(True).Max.X/s,'handedness':'right' if q.get('right_hand',True) else 'left','modeled_full_depth_degrees':q['full_degrees'],'runin_degrees':runin,'runout_degrees':runout,'root_embed_mm':.02,'bore_cut_after_thread_union':True,'vents':vent_report}
    return neck,report
