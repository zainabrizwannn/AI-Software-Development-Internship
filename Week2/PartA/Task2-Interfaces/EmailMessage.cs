public class EmailMessage : IMessage
{
    public void Send()
    {
        Console.WriteLine("Email sent successfully.");
    }
}