using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter first number");
        double num1 = Convert.ToDouble(Console.ReadLine());
        Console.Write("Enter second number");
        double num2 = Convert.ToDouble(Console.ReadLine());

        Console.WriteLine("Sum is" + (num1 + num2));
        Console.WriteLine("Difference is "+(num1 - num2));
        Console.WriteLine("Product is "+ (num1 *num2));
        Console.WriteLine("Quotient is"+ (num1/num2));

    }
}