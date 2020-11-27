using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using DiffLib;
using Python.Runtime;

namespace ConsoleApp1
{
    public class DiffExample
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("DiffExample");
            const string text1 = "This is a test of the diff implementation, with some text that is deleted.";
            const string text2 = "This is another test of the same implementation, with some more text.";
            DiffSection[] diffs = Diff.CalculateSections(text1.ToCharArray(), text2.ToCharArray()).ToArray();
            int i1 = 0;
            int i2 = 0;
            foreach (DiffSection diff in diffs) {
                //Console.WriteLine(diff);
                if(diff.IsMatch)
                {
                    Console.Write($"Matching: {text1.Substring(i1, diff.LengthInCollection1)}");
                }
                else if (diff.LengthInCollection1 == 0)
                {
                    Console.Write($"Add: {text2.Substring(i2, diff.LengthInCollection2)}");
                }
                else if (diff.LengthInCollection2 == 0)
                {
                    Console.Write($"Delete: {text1.Substring(i1, diff.LengthInCollection1)}");
                }
                else
                {
                    Console.Write($"Replace: {text1.Substring(i1, diff.LengthInCollection1)} by {text2.Substring(i2, diff.LengthInCollection2)}");
                }
                Console.WriteLine($" ({i1},{i1 + diff.LengthInCollection1}) ({i2},{i2 + diff.LengthInCollection2})");
                i1 += diff.LengthInCollection1;
                i2 += diff.LengthInCollection2;
            }
            Console.ReadLine();


            /*
            new DiffSection(isMatch: true, lengthInCollection1: 9, lengthInCollection2: 9), // same        "This is a"
            new DiffSection(isMatch: false, lengthInCollection1: 0, lengthInCollection2: 6), // add        "nother"
            new DiffSection(isMatch: true, lengthInCollection1: 13, lengthInCollection2: 13), // same      " test of the "
            new DiffSection(isMatch: false, lengthInCollection1: 4, lengthInCollection2: 4), // replace    "same" with "diff"
            new DiffSection(isMatch: true, lengthInCollection1: 27, lengthInCollection2: 27), // same      " implementation, with some "
            new DiffSection(isMatch: false, lengthInCollection1: 0, lengthInCollection2: 5), // add        "more "
            new DiffSection(isMatch: true, lengthInCollection1: 4, lengthInCollection2: 4), // same        "text"
            new DiffSection(isMatch: false, lengthInCollection1: 16, lengthInCollection2: 0), // delete    " that is deleted"
            new DiffSection(isMatch: true, lengthInCollection1: 1, lengthInCollection2: 1), // same        "."
            */
        }
    }
}
