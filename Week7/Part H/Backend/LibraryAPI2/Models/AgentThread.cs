namespace LibraryAPI.Models
{
    public class AgentThread
    {
        public string ThreadId { get; set; } = string.Empty;

        public string UserId { get; set; } = string.Empty;

        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

        // running
        // pending_approval
        // completed
        // failed
        // cancelled
        public string Status { get; set; } = "running";

        public string? UserMessage { get; set; }

        public string? PendingApprovalJson { get; set; }

        public string? FinalAnswer { get; set; }

        public string? ErrorCode { get; set; }

        public string? ErrorMessage { get; set; }

        public bool? LastApprovalDecision { get; set; }

        public bool IsCancelled { get; set; } = false;
    }
}