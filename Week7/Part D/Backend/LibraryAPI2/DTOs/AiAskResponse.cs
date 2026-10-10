namespace LibraryAPI.DTOs
{
    public class AiAskResponse
    {
        public string Answer { get; set; } = string.Empty;

        public List<string> Sources { get; set; } = new();
    }
}