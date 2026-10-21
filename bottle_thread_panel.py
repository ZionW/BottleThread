"""Rhino 8 Python 3: compact four-language thread panel."""
import math,json
from pathlib import Path
import Rhino,System
import Eto.Forms as ef
import Eto.Drawing as ed
from Rhino.UI import EtoExtensions
import scriptcontext as sc
ROOT=Path(__file__).resolve().parent
DATA=Path(System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData))/'BottleThread'
def data_path(name):
 DATA.mkdir(parents=True,exist_ok=True)
 target=DATA/name
 legacy=ROOT/name
 if not target.exists() and legacy.exists():target.write_text(legacy.read_text(encoding='utf-8'),encoding='utf-8')
 return target
engine_ns={};exec(compile((ROOT/'bottle_thread_engine.py').read_text(encoding='utf-8'),str(ROOT/'bottle_thread_engine.py'),'exec'),engine_ns)
generate=engine_ns['generate']
preview_ns={};exec(compile((ROOT/'bottle_thread_preview.py').read_text(encoding='utf-8'),str(ROOT/'bottle_thread_preview.py'),'exec'),preview_ns)
SectionPreview=preview_ns['SectionPreview']
PRESETS=json.loads((ROOT/'bottle_thread_catalog.json').read_text(encoding='utf-8'))
WORDS=json.loads((ROOT/'bottle_thread_i18n.json').read_text(encoding='utf-8'))
LANGS=['繁體中文','English','日本語','한국어']
KEY='bottle_thread_panel_v1'
GROUPS=[('dimensions',['T','E','I_test','H','pitch','c','S']),('tooth',['top','bottom','Rcrest','Rroot','full_degrees','runin','runout']),('closure',['cap_thread_depth','cap_thread_width','cap_thread_run','cap_wall','cap_top','radial_gap','axial_gap','head_gap','vent_width','vent_phase']),('position',['x','y','z'])]
DEFAULTS=dict(cap_thread_depth=.9,cap_thread_width=.5,cap_thread_run=30,runin=30,runout=30,x=0,y=0,z=0,cap_wall=1.5,cap_top=1.5,radial_gap=.2,axial_gap=.05,head_gap=.4,vent_width=1.82,vent_phase=0)
def label(text=''):
 c=ef.Label();c.Text=text;c.TextAlignment=ef.TextAlignment.Left;c.VerticalAlignment=ef.VerticalAlignment.Center;return c
def button(text=''):
 c=ef.Button();c.Text=text;return c
class ThreadPanel(ef.Form):
 def __init__(self,doc):
  super().__init__();self.doc=doc;self.loading=True;self.fields={};self.labels={};self.last_report=None;self.last_id=None;self.last_reports=[];self.last_ids=[];self.lang=0
  try:self.lang=int(json.loads(data_path('panel_preferences.json').read_text(encoding='utf-8')).get('language',0))%4
  except Exception:pass
  self.ClientSize=ed.Size(460,800);self.MinimumSize=ed.Size(450,680);self.Resizable=True
  body=ef.DynamicLayout();body.Spacing=ed.Size(8,8);body.Padding=ed.Padding(0)
  self.heading=label();self.heading.Font=ed.Font(ed.SystemFont.Bold,16);self.heading.Width=230
  self.language=ef.DropDown()
  for name in LANGS:self.language.Items.Add(name)
  self.language.SelectedIndex=self.lang;self.language.Width=150
  title_row=ef.DynamicLayout();title_row.Spacing=ed.Size(20,0);title_row.AddRow(self.heading,self.language);body.AddRow(title_row)
  self.note=label();self.note.Width=400;self.note.Wrap=ef.WrapMode.Word;self.note.Height=30;body.AddRow(self.note)
  selector=ef.DynamicLayout();selector.Spacing=ed.Size(8,6)
  self.make_neck=ef.CheckBox();self.make_cap=ef.CheckBox();self.make_neck.Checked=True;self.make_cap.Checked=False
  output_choices=ef.DynamicLayout();output_choices.Spacing=ed.Size(16,0);output_choices.AddRow(self.make_neck,self.make_cap)
  self.preset=ef.DropDown();self.style=ef.DropDown()
  for key,c in [('output',output_choices),('preset',self.preset),('style',self.style)]:
   self.labels[key]=label();self.labels[key].Width=80;c.Width=300;selector.AddRow(self.labels[key],c)
  body.AddRow(selector)
  self.source=label();self.source.Width=400;self.source.Wrap=ef.WrapMode.Word;self.source.Height=38;body.AddRow(self.source)
  self.view=ef.DropDown();self.view.Width=400;body.AddRow(self.view)
  self.preview=SectionPreview(engine_ns['build_profile']);body.AddRow(self.preview)
  self.tabs=ef.TabControl();self.tabs.Height=230;self.tabs.Width=400;self.pages={}
  self.vents=ef.CheckBox();self.vents.Checked=False
  self.cap_vents=ef.CheckBox();self.cap_vents.Checked=False
  self.hand=ef.CheckBox();self.hand.Checked=True
  for group,keys in GROUPS:
   grid=ef.DynamicLayout();grid.Padding=ed.Padding(10);grid.Spacing=ed.Size(8,7)
   if group=='closure':grid.AddRow(self.vents);grid.AddRow(self.cap_vents)
   for key in keys:
    self.labels['f_'+key]=label();self.labels['f_'+key].Width=220
    box=ef.TextBox();box.Width=100;box.TextChanged+=self.on_edit;self.fields[key]=box
    grid.AddRow(self.labels['f_'+key],box)
   if group=='position':grid.AddRow(self.hand)
   grid.AddRow(None)
   scroll=ef.Scrollable();scroll.Content=grid
   page=ef.TabPage();page.Content=scroll;self.tabs.Pages.Add(page);self.pages[group]=page
  body.AddRow(self.tabs)
  self.summary=label();self.summary.Width=400;self.summary.Height=30;self.summary.Wrap=ef.WrapMode.Word;body.AddRow(self.summary)
  main_scroll=ef.Scrollable();main_scroll.Content=body
  self.status=label();self.status.Width=400;self.status.Height=36;self.status.Wrap=ef.WrapMode.Word
  self.reset=button();self.save=button();self.check=button();self.build=button()
  buttons=ef.DynamicLayout();buttons.Spacing=ed.Size(8,6)
  buttons.AddRow(self.reset,self.save);buttons.AddRow(self.check,self.build)
  self.foot=label();self.foot.Width=400;self.foot.Height=46;self.foot.Wrap=ef.WrapMode.Word
  root=ef.TableLayout();root.Padding=ed.Padding(14);root.Spacing=ed.Size(0,8)
  for control,scale in [(main_scroll,True),(self.status,False),(buttons,False),(self.foot,False)]:
   row=ef.TableRow();row.Cells.Add(ef.TableCell(control));row.ScaleHeight=scale;root.Rows.Add(row)
  self.Content=root
  self.language.SelectedIndexChanged+=self.on_language;self.preset.SelectedIndexChanged+=self.on_preset;self.make_neck.CheckedChanged+=self.on_output;self.make_cap.CheckedChanged+=self.on_output;self.style.SelectedIndexChanged+=self.on_style;self.view.SelectedIndexChanged+=self.on_view
  self.cap_vents.CheckedChanged+=self.on_vents
  self.vents.CheckedChanged+=self.on_vents;self.hand.CheckedChanged+=self.on_edit
  self.build.Click+=self.on_generate;self.reset.Click+=self.on_preset;self.check.Click+=self.on_check;self.save.Click+=self.on_save;self.Closed+=self.on_closed
  self.localize();self.loading=False;self.preset.SelectedIndex=0;self.on_preset(None,None);self.on_output(None,None)
  EtoExtensions.UseRhinoStyle(self)
  self._doc_close_handler=self.on_document_closed
  Rhino.RhinoDoc.CloseDocument+=self._doc_close_handler
 def tr(self,key,*args):return WORDS.get(key,[key]*4)[self.lang].format(*args)
 def preset_name(self,p):
  name=p.get('name','Custom')
  if p.get('region')=='custom':name=self.tr('custom')+' '+name.replace('Custom ','')
  region=self.tr(p.get('region','custom'))
  return name+' · '+region
 def localize(self):
  old=self.loading;self.loading=True
  self.Title='Bottle Thread · '+self.tr('title');self.heading.Text=self.tr('title');self.note.Text=self.tr('subtitle')
  for key,c in self.labels.items():c.Text=self.tr(key)
  for control,items in [(self.style,[self.tr('native'),'L · 30° / 30°','M · 45° / 10°',self.tr('custom_angles')]),(self.preset,[self.preset_name(p) for p in PRESETS]),(self.view,[self.tr('section'),self.tr('tooth_view'),self.tr('vent_view')])]:
   selected=max(0,control.SelectedIndex);control.Items.Clear()
   for item in items:control.Items.Add(item)
   control.SelectedIndex=min(selected,len(items)-1)
  for key,page in self.pages.items():page.Text=self.tr(key)
  self.make_neck.Text=self.tr('neck');self.make_cap.Text=self.tr('cap')
  self.cap_vents.Text=self.tr('cap_vent_toggle');self.vents.Text=self.tr('vent_toggle');self.hand.Text=self.tr('right')
  self.reset.Text=self.tr('reset');self.save.Text=self.tr('save');self.check.Text=self.tr('check');self.update_build_button();self.foot.Text=self.tr('footer');self.preview.tr=self.tr
  self.loading=old
 def on_language(self,sender,e):
  if self.loading:return
  self.lang=max(0,self.language.SelectedIndex);self.localize();self.update_source();self.update_summary();self.status.Text=self.tr('ready')
  try:data_path('panel_preferences.json').write_text(json.dumps({'language':self.lang}),encoding='utf-8')
  except Exception:pass
 def update_source(self):
  if self.preset.SelectedIndex>=0:
   p=PRESETS[self.preset.SelectedIndex];self.source.Text=self.tr('source',p.get('drawing','CUSTOM'),self.tr(p.get('region','custom')))
 def on_view(self,sender,e):
  if self.loading:return
  self.preview.page=max(0,self.view.SelectedIndex);self.preview.Invalidate()
 def selected_outputs(self):
  return (['neck'] if self.make_neck.Checked else [])+(['cap'] if self.make_cap.Checked else [])
 def update_build_button(self):
  outputs=self.selected_outputs();key='build_pair' if len(outputs)==2 else ('build_'+outputs[0] if outputs else 'build_selected')
  self.build.Text=self.tr(key);self.build.Enabled=bool(outputs)
 def update_controls(self):
  cap=bool(self.make_cap.Checked)
  for key in ['cap_thread_depth','cap_thread_width','cap_thread_run']:self.fields[key].Enabled=cap and (PRESETS[max(0,self.preset.SelectedIndex)].get('cap_thread_model')=='independent_inward_rib' or PRESETS[max(0,self.preset.SelectedIndex)].get('id')=='pco1881')
  for key in ['cap_wall','cap_top','radial_gap','axial_gap','head_gap']:self.fields[key].Enabled=cap
  for key in ['vent_width','vent_phase']:self.fields[key].Enabled=(bool(self.make_neck.Checked) and bool(self.vents.Checked)) or (cap and bool(self.cap_vents.Checked))
  self.update_build_button()
 def on_output(self,sender,e):
  if self.loading:return
  self.update_controls();self.update_summary();self.status.Text=self.tr('pair_notice' if len(self.selected_outputs())==2 else ('ready' if self.selected_outputs() else 'select_output'))
 def on_vents(self,sender,e):
  if self.loading:return
  self.update_controls();self.update_summary()
 def on_preset(self,sender,e):
  if self.loading or self.preset.SelectedIndex<0:return
  self.loading=True;p=PRESETS[self.preset.SelectedIndex];q=dict(p)
  for key,value in DEFAULTS.items():q.setdefault(key,value)
  for key,box in self.fields.items():box.Text=str(q[key])
  self.style.SelectedIndex=0;self.vents.Checked=bool(p.get('vents',False));self.cap_vents.Checked=bool(p.get('cap_vents',p.get('vents',False)));self.hand.Checked=p.get('right_hand',True)
  self.loading=False;self.update_source();self.update_controls();self.update_summary();self.status.Text=self.tr('loaded',p['name'])
 def on_style(self,sender,e):
  if self.loading:return
  idx=self.style.SelectedIndex
  if idx==0:self.on_preset(None,None);return
  if idx in [1,2]:
   self.loading=True;self.fields['top'].Text='30' if idx==1 else '45';self.fields['bottom'].Text='30' if idx==1 else '10';self.fields['Rcrest'].Text='0.2';self.fields['Rroot'].Text='0.2';self.loading=False;self.status.Text=self.tr('style_notice')
  self.update_summary()
 def on_edit(self,sender,e):
  if self.loading:return
  self.status.Text=self.tr('edited');self.update_summary()
 def read_values(self):
  q=dict(PRESETS[max(0,self.preset.SelectedIndex)])
  for key,box in self.fields.items():
   try:q[key]=float(box.Text.strip())
   except Exception:raise ValueError(self.tr('field_error',self.tr('f_'+key)))
   if not math.isfinite(q[key]):raise ValueError(self.tr('invalid'))
  q.update(cap_vents=bool(self.cap_vents.Checked),vents=bool(self.vents.Checked),outputs=self.selected_outputs(),output='cap' if self.make_cap.Checked and not self.make_neck.Checked else 'neck',right_hand=bool(self.hand.Checked),language=self.lang,limitations=['Partial reference model, not standard certified'])
  q.setdefault('vent_angles',[-28,28,152,208]);return q
 def update_summary(self):
  try:
   q=self.read_values();self.preview.page=max(0,self.view.SelectedIndex);self.preview.update(q);self.summary.Text=self.tr('summary',(q['T']-q['E'])/2,q['full_degrees']/360,25.4/q['pitch'])
  except Exception:self.summary.Text=self.tr('invalid')
 def check_values(self):
  q=self.read_values()
  if not q['outputs']:raise ValueError(self.tr('select_output'))
  if not 0<q['I_test']<q['E']<q['T']:raise ValueError(self.tr('dimension_error'))
  if q['H']<=0 or q['pitch']<=0:raise ValueError(self.tr('invalid'))
  if 'cap' in q['outputs'] and (min(q['cap_wall'],q['cap_top'])<.3 or min(q['radial_gap'],q['axial_gap'],q['head_gap'])<0):raise ValueError(self.tr('cap_error'))
  if 'cap' in q['outputs'] and (q.get('cap_thread_model')=='independent_inward_rib' or q.get('id')=='pco1881') and not (.2<=q['cap_thread_depth']<=1.2 and .2<=q['cap_thread_width']<=1 and 10<=q['cap_thread_run']<=90):raise ValueError(self.tr('cap_tooth_error'))
  if min(q['Rcrest'],q['Rroot'])<0 or not (0<=q['top']<80 and 0<=q['bottom']<80):raise ValueError(self.tr('radius_error'))
  return q
 def error_text(self,ex):
  raw=str(ex)
  if self.lang==0:return raw
  for key in ['dimension_error','invalid','radius_error','cap_error','closed','select_output']:
   if self.tr(key)==raw:return raw
  if 'radius' in raw or '圓角' in raw:return self.tr('radius_error')
  return self.tr('geometry_error')
 def on_check(self,sender,e):
  try:self.check_values();self.status.Text=self.tr('check_ok')
  except Exception as ex:self.status.Text=self.tr('fail',self.error_text(ex))
 def on_generate(self,sender,e):
  if Rhino.RhinoDoc.FromRuntimeSerialNumber(self.doc.RuntimeSerialNumber) is None:self.status.Text=self.tr('closed');return
  self.build.Enabled=False;self.last_id=None;self.last_report=None;self.last_reports=[];self.last_ids=[];self.status.Text=self.tr('busy')
  try:
   q=self.check_values();prepared=[]
   # Complete all requested geometry before changing the document.
   for output in q['outputs']:
    partq=dict(q,output=output);b,report=generate(self.doc,partq);prepared.append((partq,b,report))
   s=Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Millimeters,self.doc.ModelUnitSystem)
   # Both parts already use the same thread phase, axis and assembled height.
   record=self.doc.BeginUndoRecord('Bottle Thread Generate')
   try:
    li=self.doc.Layers.FindByFullPath('BottleThread_UI',-1)
    if li<0:
     layer=Rhino.DocObjects.Layer();layer.Name='BottleThread_UI';li=self.doc.Layers.Add(layer)
    for partq,b,report in prepared:
     b.Transform(Rhino.Geometry.Transform.Translation(partq['x']*s,partq['y']*s,partq['z']*s))
     a=Rhino.DocObjects.ObjectAttributes();a.LayerIndex=li;a.Name=partq['name']+('_CAP_REFERENCE' if partq['output']=='cap' else '_NECK_REFERENCE');a.SetUserString('BottleThread.Parameters',json.dumps(partq,ensure_ascii=False));a.SetUserString('BottleThread.Status','Partial reference/custom prototype, not certified');oid=self.doc.Objects.AddBrep(b,a)
     if oid==System.Guid.Empty:raise RuntimeError('AddBrep failed')
     self.last_ids.append(oid);self.last_reports.append(report)
   except Exception:
    for oid in self.last_ids:self.doc.Objects.Delete(oid,True)
    self.last_ids=[];self.last_reports=[];raise
   finally:self.doc.EndUndoRecord(record)
   self.last_id=self.last_ids[-1];self.last_report=self.last_reports[-1];self.doc.Views.Redraw()
   self.status.Text=self.tr('pair_success') if len(prepared)==2 else self.tr('success',self.last_report['measured_major_diameter_mm'])
  except Exception as ex:self.status.Text=self.tr('fail',self.error_text(ex));Rhino.RhinoApp.WriteLine(str(ex))
  finally:self.update_build_button()
 def on_save(self,sender,e):
  try:
   q=self.check_values();path=data_path('custom_thread_presets.json');saved=json.loads(path.read_text(encoding='utf-8')) if path.exists() else [];q.update(name='Custom '+str(len(saved)+1),region='custom',id='saved_'+str(len(saved)+1));saved.append(q);path.write_text(json.dumps(saved,ensure_ascii=False,indent=2),encoding='utf-8');PRESETS.append(q);self.preset.Items.Add(self.preset_name(q));self.status.Text=self.tr('saved',len(saved))
  except Exception as ex:self.status.Text=self.tr('fail',self.error_text(ex))
 def on_document_closed(self,sender,e):
  if e.Document.RuntimeSerialNumber==self.doc.RuntimeSerialNumber:self.Close()
 def on_closed(self,sender,e):
  handler=getattr(self,'_doc_close_handler',None)
  if handler is not None:
   Rhino.RhinoDoc.CloseDocument-=handler;self._doc_close_handler=None
  if sc.sticky.get(KEY) is self:sc.sticky.pop(KEY,None)

def show(doc):
 if doc is None or Rhino.RhinoDoc.FromRuntimeSerialNumber(doc.RuntimeSerialNumber) is None:
  raise ValueError('Open a Rhino document before opening Bottle Thread.')
 old=sc.sticky.get(KEY)
 if old:
  try:
   owner_doc=Rhino.RhinoDoc.FromRuntimeSerialNumber(old.doc.RuntimeSerialNumber)
   if owner_doc is not None and owner_doc.RuntimeSerialNumber==doc.RuntimeSerialNumber and old.Content is not None:
    if not old.Visible:EtoExtensions.Show(old,doc)
    old.BringToFront();return old
  except Exception:pass
  try:old.Close()
  except Exception:pass
  sc.sticky.pop(KEY,None)
 path=data_path('custom_thread_presets.json')
 if path.exists():
  try:
   for i,p in enumerate(json.loads(path.read_text(encoding='utf-8'))):PRESETS.append(dict(p,name='Custom '+str(i+1),region='custom'))
  except Exception:pass
 form=ThreadPanel(doc)
 try:
  EtoExtensions.Show(form,doc);sc.sticky[KEY]=form;return form
 except Exception:
  form.Close();raise
if __name__=='__main__':show(globals().get('__rhino_doc__') or sc.doc)
