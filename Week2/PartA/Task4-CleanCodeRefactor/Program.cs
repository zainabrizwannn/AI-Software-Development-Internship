StudentManager manager = new StudentManager();
int choice = 0;
while (choice != 3)
{
    Console.WriteLine("\n===== Student Menu =====");
    Console.WriteLine("1. Add Student");
    Console.WriteLine("2. View Students");
    Console.WriteLine("3. Exit");

    Console.Write("Enter Choice: ");
    choice = Convert.ToInt32(Console.ReadLine());
    switch (choice)
    {
        case 1:
            manager.AddStudent();
            break;

        case 2:
            manager.ViewStudents();
            break;

        case 3:
            Console.WriteLine("Program Closed.");
            break;

        default:
            Console.WriteLine("Invalid Choice.");
            break;
    }
}