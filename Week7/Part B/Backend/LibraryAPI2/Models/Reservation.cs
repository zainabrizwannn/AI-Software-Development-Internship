namespace LibraryAPI.Models
{
    public class Reservation
    {
        public int Id { get; set; }
        public int BookId { get; set; }
        public string UserId { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public string IdempotencyKey { get; set; } = string.Empty;
        public Book? Book { get; set; }
    }
}