using LibraryAPI.Models;

namespace LibraryAPI.Services
{
    public interface IBookService
    {
        List<Book> GetAll();

        Book? GetById(int id);

        void Add(Book book);

        void Update(Book book);

        void Delete(int id);
    }
}