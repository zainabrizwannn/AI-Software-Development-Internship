import { Injectable } from '@angular/core';
import { Book } from '../models/book';

@Injectable({
  providedIn: 'root'
})
export class BookService {

  private books: Book[] = [
    {
      id: 1,
      title: 'Clean Code',
      author: 'Robert C. Martin',
      category: 'Programming'
    },
    {
      id: 2,
      title: 'Atomic Habits',
      author: 'James Clear',
      category: 'Self Help'
    }
  ];

  getBooks(): Book[] {
    return this.books;
  }

  addBook(book: Book): void {

    // Automatically assign the next ID
    book.id = this.books.length + 1;

    this.books.push(book);
  }

  deleteBook(id: number): void {

    // Delete the selected book
    this.books = this.books.filter(book => book.id !== id);

    // Reassign IDs
    this.books.forEach((book, index) => {
      book.id = index + 1;
    });

  }

}