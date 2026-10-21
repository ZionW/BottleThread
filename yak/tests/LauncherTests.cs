// Executes the production command against a fake Rhino host to test startup ordering.
// This checks dispatch behavior, not Rhino/Python runtime initialization.
using System;
using System.IO;
using System.Collections.Generic;
using System.Reflection;
using Rhino;
using Rhino.Commands;
using Rhino.PlugIns;
namespace Rhino {
 public class RhinoDoc { }
 public static class RhinoApp {
  public static bool DispatchResult=true;
  public static readonly List<string> Calls=new List<string>();
  public static bool RunScript(string text,bool echo) {
   if(!PlugIn.Loaded)throw new Exception("Script dispatched before service load");
   Calls.Add(text);return DispatchResult;
  }
  public static void WriteLine(string text) { }
 }
}
namespace Rhino.Commands {
 public enum Result { Success, Failure }
 public enum RunMode { Interactive }
 public enum Style { ScriptRunner }
 [AttributeUsage(AttributeTargets.Class)]
 public sealed class CommandStyleAttribute:Attribute { public CommandStyleAttribute(Style style) { } }
 public abstract class Command {
  public abstract string EnglishName { get; }
  protected abstract Result RunCommand(RhinoDoc doc,RunMode mode);
 }
}
namespace Rhino.PlugIns {
 public class PlugIn {
  public static bool Loaded,CanLoad=true;
  public static Guid Requested;
  public static bool LoadPlugIn(Guid id) { Requested=id;Loaded=CanLoad;return Loaded; }
 }
}
public static class LauncherTests {
 static void Check(bool ok,string name) { if(!ok)throw new Exception(name);Console.WriteLine("PASS: "+name); }
 static Result Run() => (Result)typeof(BottleThread.BottleThreadCommand).GetMethod("RunCommand",BindingFlags.Instance|BindingFlags.NonPublic).Invoke(new BottleThread.BottleThreadCommand(),new object[]{new RhinoDoc(),RunMode.Interactive});
 public static void Main() {
  var root=Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
  var dir=Path.GetFullPath(Path.Combine(root,"..","scripts"));Directory.CreateDirectory(dir);
  var script=Path.Combine(dir,"bottle_thread_panel.py");File.WriteAllText(script,"#! python 3\n");
  try {
   PlugIn.Loaded=false;PlugIn.CanLoad=true;RhinoApp.Calls.Clear();
   Check(Run()==Result.Success,"fresh host: load service then dispatch script");
   Check(PlugIn.Requested==new Guid("c9cba87a-23ce-4f15-a918-97645c05cde7"),"load correct built-in scripting provider");
   Check(RhinoApp.Calls.Count==1 && RhinoApp.Calls[0]=="_-ScriptEditor _Run \""+script+"\"","quoted script path, no editor-window command");
   Check(Run()==Result.Success && RhinoApp.Calls.Count==2,"repeat launch");
   PlugIn.Loaded=false;PlugIn.CanLoad=false;RhinoApp.Calls.Clear();
   Check(Run()==Result.Failure && RhinoApp.Calls.Count==0,"service load failure: do not dispatch script");
   PlugIn.CanLoad=true;RhinoApp.DispatchResult=false;
   Check(Run()==Result.Failure,"native script command failure propagated");
   File.Delete(script);RhinoApp.Calls.Clear();
   Check(Run()==Result.Failure && RhinoApp.Calls.Count==0,"missing resource: do not dispatch script");
  } finally { if(File.Exists(script))File.Delete(script); }
 }
}
