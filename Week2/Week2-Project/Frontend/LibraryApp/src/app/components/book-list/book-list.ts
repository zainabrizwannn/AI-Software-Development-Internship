import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Book } from '../../models/book';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-book-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './book-list.html',
  styleUrl: './book-list.css'
})
export class BookList {

  books: Book[] = [];

  constructor(private bookService: BookService){
    this.loadBooks();
  }

  loadBooks(){
    this.books = this.bookService.getBooks();
  }

  deleteBook(id:number){

    this.bookService.deleteBook(id);

    this.loadBooks();

    alert("Book Deleted Successfully!");

  }

}