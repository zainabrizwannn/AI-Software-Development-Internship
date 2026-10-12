namespace LibraryAPI.DTOs
{
    public class AskDto
    {
        public string Question { get; set; } = string.Empty;

        public string SessionId { get; set; } = "default-session";
    }
}