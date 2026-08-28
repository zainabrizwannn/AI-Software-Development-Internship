using System;
class Program
{
    static void Main()
    {
        Console.Write("Enter Marks");
        int marks =Convert.ToInt32(Console.ReadLine());
        Console.WriteLine("Grade: " + Grade(marks));
    }
    static string Grade(int marks)
    {
        if (marks>= 90)
            return "A";
        if (marks >= 80)
            return "B";
        if (marks >= 70)
            return "C";
        if (marks >= 60)
            return "D";
        return "F";
    }
}