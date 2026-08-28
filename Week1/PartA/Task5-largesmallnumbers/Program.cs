using System;
class Program
{
        static void Main()
    {
        int[] numbers = {12, 45, 8, 90, 23, 67, 5, 34, 78, 15};
        int largest = numbers[0];
        int smallest = numbers[0];

        for (int i = 1; i < numbers.Length; i++)
        {
            if (numbers[i] >largest)
            {
                largest =numbers[i];
            }
            if (numbers[i] <smallest)
            {
                smallest = numbers[i];
            }
        }
        Console.WriteLine("Largest number is " +largest);
        Console.WriteLine("Smallest no is " +smallest);
    }
}