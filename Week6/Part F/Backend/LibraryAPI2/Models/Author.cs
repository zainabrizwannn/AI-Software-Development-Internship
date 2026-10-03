namespace LibraryAPI.Models
{
    public class Author
    {
        public int AuthorId { get; set; }

        public string FullName { get; set; } = string.Empty;

        // Navigation Property
        public List<Book> Books { get; set; } = new();
    }
}