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
        private static readonly Guid ScriptingPluginId = new Guid("c9cba87a-23ce-4f15-a918-97645c05cde7");
        public override string EnglishName => "BottleThread";
        protected override Result RunCommand(RhinoDoc doc, RunMode mode)
        {
            try
            {
                var root = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
                var script = Path.GetFullPath(Path.Combine(root, "..", "scripts", "bottle_thread_panel.py"));
                if (!File.Exists(script)) throw new FileNotFoundException("BottleThread script is missing.", script);
                // Register Rhino's language providers before dispatching a script command.
                // Same built-in plug-in ID/load order used by McNeel's Rhino.Compute startup.
                if (!PlugIn.LoadPlugIn(ScriptingPluginId))
                    throw new InvalidOperationException("Rhino scripting service could not be loaded. See RhinoCodeLogs for details.");
                // ScriptEditor runs the file and initializes Python without opening its editor UI.
                var macro = "_-ScriptEditor _Run \"" + script + "\"";
                return RhinoApp.RunScript(macro, false) ? Result.Success : Result.Failure;
            }
            catch (Exception ex)
            {
                RhinoApp.WriteLine("BottleThread: " + ex.Message);
                RhinoApp.WriteLine("If Python initialization fails, inspect RhinoCodeLogs for the underlying error.");
                return Result.Failure;
            }
        }
    }
}
