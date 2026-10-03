namespace LibraryAPI.Models
{
    public class Book
    {
        public int BookId { get; set; }

	public string Title { get; set; } = string.Empty;

	public int AuthorId { get; set; }

	public bool IsAvailable { get; set; } = true;

	// Navigation Property
	public Author? Author { get; set; }

	// Navigation Property
	public List<Category> Categories { get; set; } = new();
	}
}