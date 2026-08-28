using System;
class Program
{
    static void Main()
    {
        int choice;
        do
        {
            Console.WriteLine("\n===MENU==");
            Console.WriteLine("1. Say Hello");
            Console.WriteLine("2. Show Current Time");
            Console.WriteLine("3. Exit");
            Console.Write("Enter your choice: ");
            choice = Convert.ToInt32(Console.ReadLine());

            switch (choice)
            {
                case 1:
                    Console.WriteLine("Hello");
                    break;

                case 2:
                    Console.WriteLine(DateTime.Now);
                    break;

                case 3:
                    Console.WriteLine("Exiting Program");
                    break;
                default:
                    Console.WriteLine("Invalid Choice");
                    break;
            }

        } while (choice!= 3);
    }
}