using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using Rhino;
using Rhino.Commands;
using Result = Rhino.Commands.Result;
using Rhino.PlugIns;
using Rhino.Runtime.Code;
using Rhino.Runtime.Code.Execution;
[assembly: Guid("bbfc1386-f3c6-46b0-a0f4-8df16576dc52")]
namespace BottleThread
{
    public sealed class BottleThreadPlugin : PlugIn { }
    [Guid("fc85e728-6b40-458d-b6d5-8d99c8587390")]
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
                var ctx = new RunContext { AutoApplyParams = true };
                ctx.Inputs["bottle_thread_document"] = doc;
                ctx.Inputs["bottle_thread_script"] = script;
                ctx.Outputs["bottle_thread_opened"] = false;
                RhinoCode.RunScript(@"#! python 3
from pathlib import Path
p = bottle_thread_script
ns = {'__file__': p, '__name__': 'bottle_thread_plugin'}
exec(compile(Path(p).read_text(encoding='utf-8'), p, 'exec'), ns)
f = ns['show'](bottle_thread_document)
bottle_thread_opened = bool(f.Visible)
", ctx);
                return ctx.Outputs.Get<bool>("bottle_thread_opened") ? Result.Success : Result.Failure;
            }
            catch (Exception ex)
            {
                RhinoApp.WriteLine("BottleThread: " + ex.Message);
                return Result.Failure;
            }
        }
    }
}
