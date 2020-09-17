using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Python.Runtime;

namespace ConsoleApp1
{
    public class Program
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("NPNearest Test"); // Compiler en AnyCPU et décocher préférer 32 bits ou compiler en x64
            Console.WriteLine("Python "+PythonEngine.Version);
            Console.WriteLine(PythonEngine.PythonPath);
            using (Py.GIL())
            {
                string npNearestPath = @"C:\Users\conta\CVC\3C-Evolution\git3ce\";
                dynamic sys = Py.Import("sys");
                sys.path.append(npNearestPath);
                dynamic config = Py.Import("config");
                Console.WriteLine($"V{config.version}");
                dynamic npnearest = Py.Import("npnearest");
                var np = npnearest.NPNearest(npNearestPath + config.h_file);
                var res = np.search(164113, 10);
                Console.WriteLine(res);
                foreach (var i in res)
                    Console.WriteLine(i[0] + " " + i[1]);
                Console.ReadKey();

            }
        }
    }
}
