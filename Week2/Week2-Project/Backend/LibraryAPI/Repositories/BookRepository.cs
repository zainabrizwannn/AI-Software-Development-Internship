using LibraryAPI.Models;

namespace LibraryAPI.Repositories
{
    public class BookRepository : IBookRepository
    {
        private readonly List<Book> books =
        [
            new Book
            {
                Id = 1,
                Title = "Clean Code",
                Author = "Robert C. Martin",
                Category = "Programming"
            },

            new Book
            {
                Id = 2,
                Title = "Atomic Habits",
                Author = "James Clear",
                Category = "Self Help"
            }
        ];

        public List<Book> GetAll()
        {
            return books;
        }

        public Book? GetById(int id)
        {
            return books.FirstOrDefault(b => b.Id == id);
        }

        public void Add(Book book)
        {
            books.Add(book);
        }

        public void Update(Book book)
        {
            var existingBook = books.FirstOrDefault(b => b.Id == book.Id);

            if (existingBook != null)
            {
                existingBook.Title = book.Title;
                existingBook.Author = book.Author;
                existingBook.Category = book.Category;
            }
        }

        public void Delete(int id)
        {
            var book = books.FirstOrDefault(b => b.Id == id);

            if (book != null)
            {
                books.Remove(book);
            }
        }
    }
}