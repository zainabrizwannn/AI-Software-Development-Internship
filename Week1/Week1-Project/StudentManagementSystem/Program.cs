using System;

class Program
{
    static void Main()
    {
        StudentManager manager = new StudentManager();
        int choice = 0;

        while (choice != 7)
        {
            Console.WriteLine("\n===== Student Management System =====");
            Console.WriteLine("1. Add Student");
            Console.WriteLine("2. View Students");
            Console.WriteLine("3. Update Student");
            Console.WriteLine("4. Delete Student");
            Console.WriteLine("5. Search Student");
            Console.WriteLine("6. Sort Students by Marks");
            Console.WriteLine("7. Exit");

            Console.Write("Enter your choice: ");

            try
            {
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
                        manager.UpdateStudent();
                        break;

                    case 4:
                        manager.DeleteStudent();
                        break;

                    case 5:
                        manager.SearchStudent();
                        break;

                    case 6:
                        manager.SortStudents();
                        break;

                    case 7:
                        Console.WriteLine("Exiting Program...");
                        break;

                    default:
                        Console.WriteLine("Invalid choice!");
                        break;
                }
            }
            catch
            {
                Console.WriteLine("Please enter a valid number.");
            }
        }
    }
}