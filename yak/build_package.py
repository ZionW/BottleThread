"""Build the AnyCPU Rhino 8 package on macOS or Windows with Rhino installed."""
from pathlib import Path
import os,shutil,subprocess
root=Path(__file__).resolve().parent
project=root/'src'/'BottleThread.csproj'
subprocess.run(['dotnet','build',str(project),'-c','Release','--no-restore','-m:1','-p:UseSharedCompilation=false'],check=True)
stage=root/'stage'
if stage.exists():shutil.rmtree(stage)
stage.mkdir()
for tfm in ['net7.0','net48']:
 (stage/tfm).mkdir();shutil.copy2(root/'src'/'bin'/'Release'/tfm/'BottleThread.rhp',stage/tfm/'BottleThread.rhp')
(stage/'scripts').mkdir()
for name in ['bottle_thread_panel.py','bottle_thread_preview.py','bottle_thread_engine.py','bottle_thread_catalog.json','bottle_thread_i18n.json']:
 shutil.copy2(root.parent/name,stage/'scripts'/name)
shutil.copy2(root/'manifest.yml',stage/'manifest.yml')
shutil.copy2(root/'INSTALL.md',stage/'INSTALL.md')
yak=os.environ.get('BOTTLETHREAD_YAK') or (str(Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Rhino 8'/'System'/'Yak.exe') if os.name=='nt' else '/Applications/Rhino 8.app/Contents/Resources/bin/yak')
subprocess.run([yak,'build','--platform','any'],cwd=stage,check=True)
(root/'dist').mkdir(exist_ok=True)
for p in stage.glob('*.yak'):shutil.copy2(p,root/'dist'/p.name);print(root/'dist'/p.name)
