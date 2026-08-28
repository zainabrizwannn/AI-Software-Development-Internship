public class Teacher : Person
{
    public String Subject;

    public Teacher(String name, int age, String subject):base( name, age)
    {
        Subject = subject;
    }
    public void showTeachers()
    {
        Display();
        Console.WriteLine("subject teaching is: "+Subject);
    }
}