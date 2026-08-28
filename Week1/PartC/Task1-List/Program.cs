using System;
using System.Collections.Generic;
class Program
{
    static void Main()
    {
        List<Student> students = new List<Student>();

        students.Add(new Student(1, "Ali", "CS", 85));
        students.Add(new Student(2, "Sara", "IT", 90));
        students.Add(new Student(3, "Ahmed", "CS", 78));
        students.Add(new Student(4, "Ayesha", "SE", 88));
        students.Add(new Student(5, "Zainab", "IT", 95));

        Console.WriteLine("Student List:");
        foreach (Student student in students)
        {
            Console.WriteLine(student.Id + " " + student.Name + " " + student.Department + " " + student.Marks);
        }
    }
}