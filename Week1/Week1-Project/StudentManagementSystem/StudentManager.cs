using System;
using System.Collections.Generic;
using System.Linq;
public class StudentManager
{
                    // list of students
    private List<Student> students = new List<Student>();

                    //add the students
    public void AddStudent()
    {
        Console.Write("Enter ID: ");
        int id = Convert.ToInt32(Console.ReadLine());

        Console.Write("Enter Name: ");
        string name = Console.ReadLine();

        Console.Write("Enter Department: ");
        string department = Console.ReadLine();

        Console.Write("Enter Marks: ");
        int marks = Convert.ToInt32(Console.ReadLine());

        Student student = new Student(id, name, department, marks);

        students.Add(student);

        Console.WriteLine("Student added successfully!");
    }

                    //view students
    public void ViewStudents()
{
    if (students.Count == 0)
    {
        Console.WriteLine("No students found.");
        return;
    }

    Console.WriteLine("\nStudent List:");

    foreach (Student student in students)
    {
        Console.WriteLine("ID: " + student.Id);
        Console.WriteLine("Name: " + student.Name);
        Console.WriteLine("Department: " + student.Department);
        Console.WriteLine("Marks: " + student.Marks);
        Console.WriteLine("----------------------");
    }
}

            // UPDATE STUDENTS
public void UpdateStudent()
{
    Console.Write("Enter Student ID to update: ");
    int id = Convert.ToInt32(Console.ReadLine());

    Student student = students.Find(s => s.Id == id);

    if (student != null)
    {
        Console.Write("Enter New Name: ");
        student.Name = Console.ReadLine();

        Console.Write("Enter New Department: ");
        student.Department = Console.ReadLine();

        Console.Write("Enter New Marks: ");
        student.Marks = Convert.ToInt32(Console.ReadLine());

        Console.WriteLine("Student updated successfully!");
    }
    else
    {
        Console.WriteLine("Student not found.");
    }
}

            //DELETE STUDENTSS
public void DeleteStudent()
{
    Console.Write("Enter Student ID to delete: ");
    int id = Convert.ToInt32(Console.ReadLine());

    Student student = students.Find(s => s.Id == id);

    if (student != null)
    {
        students.Remove(student);
        Console.WriteLine("Student deleted successfully!");
    }
    else
    {
        Console.WriteLine("Student not found.");
    }
}

            // SEARCH STUDENTS
public void SearchStudent()
{
    Console.Write("Enter Student ID to search: ");
    int id = Convert.ToInt32(Console.ReadLine());

    Student student = students.FirstOrDefault(s => s.Id == id);

    if (student != null)
    {
        Console.WriteLine("ID: " + student.Id);
        Console.WriteLine("Name: " + student.Name);
        Console.WriteLine("Department: " + student.Department);
        Console.WriteLine("Marks: " + student.Marks);
    }
    else
    {
        Console.WriteLine("Student not found.");
    }
}

            // SORT STUDENTS 
public void SortStudents()
{
    var sortedStudents = students.OrderBy(s => s.Marks);

    Console.WriteLine("\nStudents Sorted by Marks:");

    foreach (Student student in sortedStudents)
    {
        Console.WriteLine(student.Id + " " +
                          student.Name + " " +
                          student.Department + " " +
                          student.Marks);
    }
}


}