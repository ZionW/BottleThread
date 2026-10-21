import math
import Rhino
import Eto.Forms as ef
import Eto.Drawing as ed

class Diagram(ef.Drawable):
 def __init__(self,profile_builder):
  super().__init__();self.Height=140;self.Width=148;self.page=0;self.q=None;self.curve=None;self.tr=lambda k,*a:k;self.profile_builder=profile_builder;self.error=None
 def update(self,q):
  self.q=dict(q);self.error=None
  try:
   p=dict(q);p['ext']=max(.05,p['Rroot']*max(math.tan(math.radians((90-p['top'])/2)),math.tan(math.radians((90-p['bottom'])/2)))+.03)
   self.curve=self.profile_builder(p,1,.0001)
   self.cap_curve=None
   if (q.get('cap_thread_model')=='independent_inward_rib' or q.get('id')=='pco1881'):
    cp=dict(p,E=.04,T=2*(q.get('cap_thread_depth',.9)+.02),c=q.get('cap_thread_width',.5),top=q['bottom'],bottom=q['top'],Rcrest=.1,Rroot=.1,ext=.15)
    self.cap_curve=self.profile_builder(cp,1,.0001)
    self.cap_curve.Transform(Rhino.Geometry.Transform.Mirror(Rhino.Geometry.Plane(Rhino.Geometry.Point3d.Origin,Rhino.Geometry.Vector3d.XAxis)))
    self.cap_curve.Transform(Rhino.Geometry.Transform.Translation(q['T']/2+q['radial_gap']+.02,0,0))
  except Exception as ex:self.curve=None;self.error=str(ex)
  self.Invalidate()
 def OnPaint(self,e):
  super().OnPaint(e);g=e.Graphics;w=max(140,self.Width);cx=w/2
  bg=ed.Color.FromArgb(247,249,252);ink=ed.Color.FromArgb(38,52,68);blue=ed.Color.FromArgb(25,102,167);orange=ed.Color.FromArgb(211,111,40)
  g.FillRectangle(ed.SolidBrush(bg),0,0,w,self.Height);font=ed.Font(ed.SystemFont.Default,10);pen=ed.Pen(blue,1.6);thin=ed.Pen(ed.Color.FromArgb(157,171,185),1)
  def text(x,y,t,color=ink):g.DrawText(font,color,float(x),float(y),str(t))
  def path(points,p=pen,close=False):
   gp=ed.GraphicsPath();gp.MoveTo(float(points[0][0]),float(points[0][1]))
   for x,y in points[1:]:gp.LineTo(float(x),float(y))
   if close:gp.CloseFigure()
   g.DrawPath(p,gp);gp.Dispose()
  if not self.q:text(12,15,self.tr('ready'));return
  q=self.q;self.draw_error=None
  try:
   if self.page==0 and (q.get('assembled') or (q.get('output')=='cap' and (q.get('cap_thread_model')=='independent_inward_rib' or q.get('id')=='pco1881'))):
    # Common axis and scale: cap ceiling sits above the neck mouth by head_gap.
    ro=q['T']/2+q['radial_gap']+q['cap_wall'];ceiling=q['H']+q['head_gap']+q['axial_gap'];ztop=ceiling+q['cap_top'];k=min(62/ro,118/ztop)
    def xy(r,z):return (cx+r*k,130-z*k)
    cap_pen=ed.Pen(orange,1.6);root=q['E']/2;inside=q['I_test']/2;gap=q['radial_gap']
    centers=[];total=q['full_degrees']+q['runin']+q['runout']
    for turn in range(int(total/360)+1):
     if turn*360<=total:centers.append(q['H']-q['S']-q['c']/2-turn*q['pitch'])
    tooth=[]
    if self.curve:
     for seg in self.curve.DuplicateSegments():
      for j in range(17):
       pt=seg.PointAt(seg.Domain.ParameterAt(j/16.0))
       if pt.X>=root-.021:tooth.append((max(root,pt.X),pt.Z))
    for sign in [-1,1]:
     if q.get('assembled'):
      path([xy(sign*root,q['H']),xy(sign*inside,q['H']),xy(sign*inside,0),xy(sign*root,0)],close=True)
      for zc in centers:
       points=[xy(sign*x,zc+z) for x,z in tooth if 0<zc+z<q['H']]
       if points:path(points)
     if (q.get('cap_thread_model')=='independent_inward_rib' or q.get('id')=='pco1881'):
      base=q['T']/2+gap;cappts=[]
      for seg in self.cap_curve.DuplicateSegments():
       for j in range(17):
        pt=seg.PointAt(seg.Domain.ParameterAt(j/16.0))
        if pt.X<=base+.021:cappts.append((min(base,pt.X),pt.Z))
      inner=[xy(sign*base,0)]
      for zc in sorted(centers):
       inner.extend(xy(sign*x,zc-q['pitch']/2+z) for x,z in cappts if 0<zc-q['pitch']/2+z<q['H'])
     else:
      base=root+gap;inner=[xy(sign*base,0)]
      for zc in sorted(centers):inner.extend(xy(sign*(x+gap),zc+z+(q['axial_gap'] if z>=0 else -q['axial_gap'])) for x,z in tooth if 0<zc+z<q['H'])
     inner.append(xy(sign*base,ceiling));path(inner,cap_pen)
     path([xy(sign*ro,0),xy(sign*ro,ztop)],cap_pen)
     path([xy(sign*ro,0),xy(sign*base,0)],cap_pen)
    path([xy(-ro,ztop),xy(ro,ztop)],cap_pen)
    path([xy(-base,ceiling),xy(base,ceiling)],cap_pen)
   elif self.page==0:
    top=20;h=104;k=min(4,62/(q['T']/2+q.get('cap_wall',1.5)+q.get('radial_gap',.2)))
    if q.get('output')=='cap':
     ro=(q['T']/2+q['radial_gap']+q['cap_wall'])*k;ri=(q['E']/2+q['radial_gap'])*k;lid=max(6,q['cap_top']*k)
     path([(cx-ro,top+h),(cx-ro,top),(cx+ro,top),(cx+ro,top+h),(cx+ri,top+h),(cx+ri,top+lid),(cx-ri,top+lid),(cx-ri,top+h)],close=True)
    else:
     rr=q['E']/2*k;ri=q['I_test']/2*k
     for sign in [-1,1]:
      a=cx+sign*rr;b=cx+sign*ri;path([(a,top),(b,top),(b,top+h),(a,top+h)],close=True)
     for j in range(3):
      yy=top+24+j*27;path([(cx+rr,yy-6),(cx+q['T']/2*k,yy-2),(cx+q['T']/2*k,yy+2),(cx+rr,yy+6)])
   elif self.page==1:
    active_curve=self.cap_curve if q.get('output')=='cap' and (q.get('cap_thread_model')=='independent_inward_rib' or q.get('id')=='pco1881') else self.curve
    if not active_curve:text(12,70,self.tr('profile_bad'),orange);return
    pts=[]
    for seg in active_curve.DuplicateSegments():
     for j in range(31):
      p=seg.PointAt(seg.Domain.ParameterAt(j/30.0));pts.append((p.X,p.Z))
    xmin=min(x for x,z in pts);xmax=max(x for x,z in pts);zmin=min(z for x,z in pts);zmax=max(z for x,z in pts);k=min(120/max(xmax-xmin,.1),110/max(zmax-zmin,.1));mx=(xmin+xmax)/2;mz=(zmin+zmax)/2
    path([(cx+(x-mx)*k,76-(z-mz)*k) for x,z in pts],close=True)
   else:
    capview=q.get('output')=='cap';both=q.get('assembled',False);outer=q['T']/2+q['radial_gap']+q['cap_wall'];cy=78;k=54/max(outer if capview or both else q['T']/2,.1)
    angles=q.get('vent_angles',[-28,28,152,208]);phase=q.get('vent_phase',0);width=q.get('vent_width',1.82)
    def ring(base,tip,enabled,color):
     points=[];half=math.degrees(math.asin(min(.9,width/(2*base))))
     for i in range(721):
      a=i/2;gap=enabled and any(abs((a-v-phase+180)%360-180)<half for v in angles);r=(base if gap else tip)*k;points.append((cx+r*math.sin(math.radians(a)),cy-r*math.cos(math.radians(a))))
     path(points,ed.Pen(color,1.5),True)
    if not capview or both:
     ring(q['E']/2+.01,q['T']/2,q.get('vents',False),blue);ir=q['I_test']/2*k;g.DrawEllipse(thin,cx-ir,cy-ir,2*ir,2*ir)
    if capview or both:
     base=q['T']/2+q['radial_gap'];d=q.get('cap_thread_depth',.9) if (q.get('cap_thread_model')=='independent_inward_rib' or q.get('id')=='pco1881') else (q['T']-q['E'])/2
     ring(base-.01,base-d,q.get('cap_vents',q.get('vents',False)),orange);g.DrawEllipse(ed.Pen(orange,1),cx-outer*k,cy-outer*k,2*outer*k,2*outer*k)
    text(cx-30,4,self.tr('start'))
  except Exception as ex:self.draw_error=str(ex);text(12,60,self.tr('invalid'),orange)

class PreviewRow(ef.Panel):
 def __init__(self,profile_builder):
  super().__init__();self.Height=140;self.Width=400
  self.diagram=Diagram(profile_builder);self.info=ef.Label();self.info.Width=238;self.info.Wrap=ef.WrapMode.Word;self.info.TextAlignment=ef.TextAlignment.Left;self.info.VerticalAlignment=ef.VerticalAlignment.Center
  layout=ef.DynamicLayout();layout.Spacing=ed.Size(12,0);layout.AddRow(self.diagram,self.info);self.Content=layout
 @property
 def tr(self):return self.diagram.tr
 @tr.setter
 def tr(self,value):self.diagram.tr=value
 @property
 def page(self):return self.diagram.page
 @page.setter
 def page(self,value):self.diagram.page=value
 @property
 def error(self):return self.diagram.error
 def update(self,q):self.diagram.update(q);self.refresh_info()
 def Invalidate(self):self.diagram.Invalidate();self.refresh_info()
 def refresh_info(self):
  q=self.diagram.q
  if not q:self.info.Text=self.tr('ready');return
  if self.page==0:
   if q.get('output')=='cap':
    keys=['cap_wall','cap_top','radial_gap','axial_gap','head_gap']
    if (q.get('cap_thread_model')=='independent_inward_rib' or q.get('id')=='pco1881'):keys=['cap_thread_depth','cap_thread_width','radial_gap','axial_gap','head_gap'];lines=[self.tr('f_'+k)+'  %.2f mm'%q[k] for k in keys]
   else:lines=['T  %.2f / E  %.2f mm'%(q['T'],q['E']),'I  %.2f / H  %.2f mm'%(q['I_test'],q['H']),'S  %.2f mm'%q['S'],'P  %.3f mm'%q['pitch']]
   lines.append(self.tr('schematic'))
  elif self.page==1:
   lines=[self.tr('f_'+k)+'  '+('%.1f°'%q[k] if k in ['top','bottom'] else '%.3f mm'%q[k]) for k in ['top','bottom','Rcrest','Rroot','c']]
   if q.get('output')=='cap' and (q.get('cap_thread_model')=='independent_inward_rib' or q.get('id')=='pco1881'):
    lines=[self.tr('f_cap_thread_depth')+' %.2f mm'%q.get('cap_thread_depth',.9),self.tr('f_cap_thread_width')+' %.2f mm'%q.get('cap_thread_width',.5),self.tr('f_top')+' %.1f°'%q['bottom'],self.tr('f_bottom')+' %.1f°'%q['top'],'R 0.10 mm',self.tr('schematic')]
  else:
   enabled=q.get('cap_vents',q.get('vents',False)) if q.get('output')=='cap' else q.get('vents',False);lines=[self.tr('vents_on',q.get('vent_width',1.82)) if enabled else self.tr('vents_off')]
   if enabled:lines.append(self.tr('phase',q.get('vent_phase',0)))
   lines.append(self.tr('mating') if q.get('output')=='cap' else self.tr('schematic'))
  self.info.Text='\n'.join(lines)

class SectionPreview(ef.Panel):
 def __init__(self,profile_builder):
  super().__init__();self.Width=400;self.Height=140;self._page=0;self._tr=lambda k,*a:k;self.q=None
  self.rows=[PreviewRow(profile_builder),PreviewRow(profile_builder)]
  self.diagram=self.rows[0].diagram;self.info=self.rows[0].info
  self.layout=ef.DynamicLayout();self.layout.Spacing=ed.Size(0,6)
  for row in self.rows:self.layout.AddRow(row)
  self.rows[1].Visible=False;self.Content=self.layout
 @property
 def tr(self):return self._tr
 @tr.setter
 def tr(self,value):
  self._tr=value
  for row in self.rows:row.tr=value
 @property
 def page(self):return self._page
 @page.setter
 def page(self,value):
  self._page=value
  for row in self.rows:row.page=value
 @property
 def error(self):return next((row.error for row in self.rows if row.Visible and row.error),None)
 def update(self,q):
  self.q=dict(q);outputs=q.get('outputs',[q.get('output','neck')]);self.displayed_outputs=list(outputs)
  self.Height=140
  for i,row in enumerate(self.rows):
   row.Visible=i==0 and bool(outputs)
   if row.Visible:row.update(dict(q,output=outputs[0],assembled=len(outputs)==2))
  self.refresh_info()
 def refresh_info(self):
  for row in self.rows:
   if row.Visible:
    row.refresh_info()
    if row.diagram.q:
     if row.diagram.q.get('assembled'):
      q=row.diagram.q
      if self.page==0:row.info.Text=self.tr('pair_legend')+'\nT %.2f / E %.2f mm'%(q['T'],q['E'])+'\n'+self.tr('f_radial_gap')+' %.2f mm'%q['radial_gap']+'\n'+self.tr('f_axial_gap')+' %.2f mm'%q['axial_gap']+'\n'+self.tr('f_head_gap')+' %.2f mm'%q['head_gap']+'\n'+self.tr('schematic')
      elif self.page==2:row.info.Text=self.tr('pair_legend')+'\n'+self.tr('neck')+': '+(self.tr('vents_on',q['vent_width']) if q.get('vents',False) else self.tr('vents_off'))+'\n'+self.tr('cap')+': '+(self.tr('vents_on',q['vent_width']) if q.get('cap_vents',q.get('vents',False)) else self.tr('vents_off'))+'\n'+self.tr('phase',q['vent_phase'])+'\n'+self.tr('schematic')
      else:row.info.Text=self.tr('neck')+' / '+self.tr('cap')+'\n'+row.info.Text
     else:row.info.Text=self.tr(row.diagram.q['output'])+'\n'+row.info.Text
 def Invalidate(self):
  for row in self.rows:
   if row.Visible:row.diagram.Invalidate()
  self.refresh_info()
