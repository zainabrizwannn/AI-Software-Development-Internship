using LibraryAPI.Clients;
using LibraryAPI.DTOs;
using Microsoft.AspNetCore.Mvc;
using Polly.CircuitBreaker;
using Polly.Timeout;

namespace LibraryAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AssistantController : ControllerBase
    {
        private readonly IAiServiceClient _aiServiceClient;

        public AssistantController(
            IAiServiceClient aiServiceClient
        )
        {
            _aiServiceClient = aiServiceClient;
        }

        [HttpPost("ask")]
        public async Task<IActionResult> Ask(
            AskDto dto
        )
        {
            if (string.IsNullOrWhiteSpace(dto.Question))
            {
                return BadRequest(
                    new
                    {
                        message = "Question is required."
                    }
                );
            }

            try
            {
                var result =
                    await _aiServiceClient.AskAsync(
                        dto.Question
                    );

                return Ok(result);
            }
            catch (BrokenCircuitException)
            {
                return StatusCode(
                    503,
                    new
                    {
                        message =
                            "The AI assistant is temporarily unavailable. Please try again shortly."
                    }
                );
            }
            catch (TimeoutRejectedException)
            {
                return StatusCode(
                    503,
                    new
                    {
                        message =
                            "The AI assistant took too long to respond. Please try again shortly."
                    }
                );
            }
            catch (HttpRequestException)
            {
                return StatusCode(
                    503,
                    new
                    {
                        message =
                            "The AI assistant is temporarily unavailable. Please try again shortly."
                    }
                );
            }
        }
    }
}