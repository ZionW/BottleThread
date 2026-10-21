using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using Rhino;
using Rhino.Commands;
using Result = Rhino.Commands.Result;
using Rhino.PlugIns;
[assembly: Guid("bbfc1386-f3c6-46b0-a0f4-8df16576dc52")]
namespace BottleThread
{
    public sealed class BottleThreadPlugin : PlugIn { }
    [Guid("fc85e728-6b40-458d-b6d5-8d99c8587390")]
    [CommandStyle(Style.ScriptRunner)]
    public sealed class BottleThreadCommand : Command
    {
        public override string EnglishName => "BottleThread";
        protected override Result RunCommand(RhinoDoc doc, RunMode mode)
        {
            try
            {
                var root = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
                var script = Path.GetFullPath(Path.Combine(root, "..", "scripts", "bottle_thread_panel.py"));
                if (!File.Exists(script)) throw new FileNotFoundException("BottleThread script is missing.", script);
                // The public command entry loads/initializes Rhino's language provider.
                // Direct RhinoCode.RunScript can fail on a fresh session before it is registered.
                var macro = "_-ScriptEditor _Run \"" + script + "\"";
                return RhinoApp.RunScript(macro, false) ? Result.Success : Result.Failure;
            }
            catch (Exception ex)
            {
                RhinoApp.WriteLine("BottleThread: " + ex.Message);
                RhinoApp.WriteLine("Run ScriptEditor once and let Python 3 finish initialization, then retry BottleThread.");
                return Result.Failure;
            }
        }
    }
}
