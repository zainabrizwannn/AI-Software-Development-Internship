namespace LibraryAPI.Models
{
    public class Book
    {
        public int BookId { get; set; }

        public string Title { get; set; } = string.Empty;

        public int AuthorId { get; set; }

        // Navigation Property
        public Author? Author { get; set; }

        // Navigation Property
        public List<Category> Categories { get; set; } = new();
    }
}