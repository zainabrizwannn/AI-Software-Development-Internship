using Microsoft.AspNetCore.Mvc;

namespace Task3_StatusCodes.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class StudentsController : ControllerBase
    {
        private static List<string> students = new List<string>
        {
            "Ali",
            "Ayesha",
            "Maaz"
        };

        // 200 OK
        [HttpGet]
        public IActionResult GetStudents()
        {
            return Ok(students);
        }

        // 201 Created
        [HttpPost]
        public IActionResult AddStudent([FromBody] string name)
        {
            students.Add(name);
            return Created("", $"{name} added successfully.");
        }

        // 400 Bad Request
        [HttpGet("check")]
        public IActionResult CheckAge(int age)
        {
            if (age < 18)
            {
                return BadRequest("Age must be 18 or above.");
            }

            return Ok("Valid Age");
        }

        // 404 Not Found
        [HttpGet("{id}")]
        public IActionResult GetStudent(int id)
        {
            if (id < 0 || id >= students.Count)
            {
                return NotFound("Student not found.");
            }

            return Ok(students[id]);
        }
    }
}