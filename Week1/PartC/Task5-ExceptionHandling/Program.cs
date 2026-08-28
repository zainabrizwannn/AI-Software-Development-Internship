using System;
class Program
{
    static void Main()
    {
        try
        {
            Console.Write("Enter a number: ");
            int number = Convert.ToInt32(Console.ReadLine());
            Console.WriteLine("You entered " + number);
        }
        catch
        {
            Console.WriteLine("Invalid input, please enter any number");
        }
        finally
        {
            Console.WriteLine("Program ended");
        }
    }
}