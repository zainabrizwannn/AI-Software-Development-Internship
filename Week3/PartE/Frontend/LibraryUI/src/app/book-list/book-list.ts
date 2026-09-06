import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

import { Book } from '../models/book';
import { BookService } from '../services/book.service';

@Component({
  selector: 'app-book-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './book-list.html',
  styleUrls: ['./book-list.css']
})
export class BookListComponent implements OnInit {

  books: Book[] = [];
  isLoading = false;
  errorMessage = '';

  bookForm: FormGroup;

  constructor(
    private bookService: BookService,
    private fb: FormBuilder
  ) {
    this.bookForm = this.fb.group({
      title: ['', Validators.required],
      authorId: [0, Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadBooks();
  }

  loadBooks(): void {
    this.isLoading = true;

    this.bookService.getBooks().subscribe({
      next: (data) => {
  console.log(data);
  this.books = data;
  this.isLoading = false;

  console.log(this.isLoading);
},
      error: (err) => {
        console.error(err);
        this.errorMessage = 'Could not load books.';
        this.isLoading = false;
      }
    });
  }

  addBook(): void {

    if (this.bookForm.invalid) {
      return;
    }

    this.bookService.addBook(this.bookForm.value).subscribe({
      next: () => {
        this.loadBooks();

        this.bookForm.reset({
          title: '',
          authorId: 0
        });
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = 'Could not save book.';
      }
    });

  }

}