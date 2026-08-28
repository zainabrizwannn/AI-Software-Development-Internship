using System;
class Program
{
      static void Main()
    {
        Student student = new Student("Maaz", 20, 101);
        Teacher teacher = new Teacher("Zainab", 35, "Math");
        Console.WriteLine("Student Details are ");
        student.ShowStudents();

        Console.WriteLine("Teacher Details are");
        teacher.showTeachers();
    }
}