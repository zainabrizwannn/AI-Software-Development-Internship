public class Person
{
    public string Name {get; set;}
    public int Age {get; set;}

    public Person(string name, int age)
    {
        Name = name;
        Age= age;
    }

    public void Display()
    {
        Console.WriteLine("Name is "+Name);
        Console.WriteLine("Age is "+Age);

    }
}