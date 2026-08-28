public class Student: Person
{
    public int RollNo {get; set;}

    public Student(string name, int age, int rollno): base(name, age)
    {
        RollNo = rollno;
    }

    public void ShowStudents()
    {
        Display();
        Console.WriteLine("RollNo "+RollNo);
    }
}