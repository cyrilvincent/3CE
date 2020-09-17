using Python.Runtime;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApp1
{
    class Program
    {
        static void Main(string[] args)
        {
            using (Py.GIL())
            {
                Environment.SetEnvironmentVariable("PYTHONPATH", @"C:\Users\conta\CVC\3C-Evolution\git3ce");
                PythonEngine.PythonPath = Environment.GetEnvironmentVariable("PYTHONPATH");
                dynamic sys = Py.Import("sys");
                sys.path.append(@"C:\Users\conta\CVC\3C-Evolution\git3ce");
                dynamic config = Py.Import("config");
                Console.WriteLine(config.version);
                dynamic npnearest = Py.Import("npnearest");
                dynamic np = npnearest.NPNearest(@"C:\Users\conta\CVC\3C-Evolution\git3ce\data\data.h.pickle");
                dynamic res = np.search(164113, 10);
                Console.WriteLine(res);

                dynamic npparser = Py.Import("npparser");
                dynamic p = npparser.NPParser();
                p.parse(@"C:\Users\conta\CVC\3C-Evolution\git3ce\data\data.txt");
                p.normalize();
                p.h();
                p.save(prefix: "net");

                Console.ReadKey();

            }
        }
    }
}
