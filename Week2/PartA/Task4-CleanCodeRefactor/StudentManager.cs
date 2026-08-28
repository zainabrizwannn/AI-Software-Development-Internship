using System;
using System.Collections.Generic;

public class StudentManager
{
    private List<Student> students = new List<Student>();

    public void AddStudent()
    {
        Student student = new Student();

        Console.Write("Enter ID: ");
        student.Id = Convert.ToInt32(Console.ReadLine());

        Console.Write("Enter Name: ");
        student.Name = Console.ReadLine()!;

        Console.Write("Enter Marks: ");
        student.Marks = Convert.ToDouble(Console.ReadLine());

        students.Add(student);

        Console.WriteLine("Student added successfully.");
    }

    public void ViewStudents()
    {
        if (students.Count == 0)
        {
            Console.WriteLine("No students found.");
            return;
        }

        foreach (Student student in students)
        {
            Console.WriteLine("-------------------------");
            Console.WriteLine($"ID: {student.Id}");
            Console.WriteLine($"Name: {student.Name}");
            Console.WriteLine($"Marks: {student.Marks}");
        }
    }
}