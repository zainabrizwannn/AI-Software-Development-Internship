using System;
public class Student: IPrintable
{
    public string Name {get; set;}

    public Student(string name)
    {
        Name = name;
    }

    public void Print()
    {
        Console.WriteLine("Students name is "+Name);
    }
}
