namespace LibraryAPI.Dtos
{
    public class StartAgentRunRequest
    {
        public string Message { get; set; } = string.Empty;
    }

    public class ResumeAgentRunRequest
    {
        public bool Approved { get; set; }
    }

    public class AgentRunStateResponse
    {
        public string ThreadId { get; set; } = string.Empty;

        public string Status { get; set; } = string.Empty;

        public string? UserMessage { get; set; }

        public object? PendingApproval { get; set; }

        public string? FinalAnswer { get; set; }

        public string? ErrorCode { get; set; }

        public string? ErrorMessage { get; set; }

        public bool IsCancelled { get; set; }

        public DateTime CreatedAt { get; set; }

        public DateTime UpdatedAt { get; set; }
    }
}