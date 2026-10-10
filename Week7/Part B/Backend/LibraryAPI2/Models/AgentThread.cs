namespace LibraryAPI.Models
{
    public class AgentThread
    {
        public string ThreadId { get; set; } = string.Empty;

        public string UserId { get; set; } = string.Empty;

        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}