using Microsoft.AspNetCore.Mvc;

namespace Task1_FirstAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class HelloController : ControllerBase
    {
        // GET: api/Hello
        [HttpGet]
        public IActionResult GetMessage()
        {
            return Ok("Hello! Welcome to ASP.NET Core Web API.");
        }

        // POST: api/Hello
        [HttpPost]
        public IActionResult SayHello([FromBody] User user)
        {
            return Ok($"Hello {user.Name}!");
        }
    }

    public class User
    {
        public string Name { get; set; } = "";
    }
}