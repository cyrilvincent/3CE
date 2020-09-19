using Python.Runtime;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ConsoleApp1
{
    class ThreadTestMain
    {

        static dynamic np = null;
        static void Main(string[] args)
        {
            Console.WriteLine("NPNearest Thread Test");
            using (Py.GIL())
            {
                dynamic sys = Py.Import("sys");
                sys.path.append(@"C:\Users\conta\CVC\3C-Evolution\git3ce");
                dynamic npnearest = Py.Import("npnearest");
                np = npnearest.NPNearest(@"C:\Users\conta\CVC\3C-Evolution\git3ce\data\data.h.pickle",false);
                Thread t1 = new Thread(new ThreadStart(ThreadFn));
                t1.Start();
                dynamic config = Py.Import("config");
                Console.WriteLine(config.version);
                Thread t2 = new Thread(new ThreadStart(ThreadFn));
                t2.Start();
                while (true) {
                    var res = np.search(164113, 10);
                    Console.WriteLine(res);
                }
            }
        }

        static void ThreadFn()
        {
            using (Py.GIL())
            {
                while (true)
                {
                    var res = np.search(164114, 10);
                    Console.WriteLine(res);
                }
            }
        }
    }
}
