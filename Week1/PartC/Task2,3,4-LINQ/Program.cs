using System;
using System.Collections.Generic;
using System.Linq;
class Program
{
    static void Main()
    {
        List<Student> students =new List<Student>()
        {
            new Student(1, "Ali", "CS", 85),
            new Student(2, "Maaz", "CYS", 90),
            new Student(3, "Ahmed", "CS", 78),
            new Student(4, "Eman", "SE", 88),
            new Student(5, "Zainab", "IS", 95)
        };
        // Find students of CS 
        Console.WriteLine("CS Students:");
        var csStudents = students.Where(s => s.Department == "CS");

        foreach (var student in csStudents)
        {
            Console.WriteLine(student.Name);
        }
        // Sort students by marks
        Console.WriteLine("\nStudents Sorted by Marks:");
        var sortedStudents = students.OrderBy(s => s.Marks);
        foreach (var student in sortedStudents)
        {
            Console.WriteLine(student.Name + " - " + student.Marks);
        }

        // Find student by ID
        Console.WriteLine("\nFind Student by ID");
        Console.Write("Enter ID: ");
        int id = Convert.ToInt32(Console.ReadLine());
        var foundStudent = students.FirstOrDefault(s => s.Id == id);

        if (foundStudent != null)
        {
            Console.WriteLine("Name: " + foundStudent.Name);
            Console.WriteLine("Department: " + foundStudent.Department);
            Console.WriteLine("Marks: " + foundStudent.Marks);
        }
        else
        {
            Console.WriteLine("Student not found.");
        }
    }
}