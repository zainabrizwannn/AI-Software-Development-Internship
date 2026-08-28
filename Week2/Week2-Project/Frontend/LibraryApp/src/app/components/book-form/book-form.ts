import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-book-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './book-form.html',
  styleUrl: './book-form.css'
})
export class BookForm {

  private fb = inject(FormBuilder);

  constructor(private bookService: BookService){}

bookForm = this.fb.group({

  title:['',[
    Validators.required,
    Validators.minLength(3)
  ]],

  author:['',[
    Validators.required
  ]],

  category:['',[
    Validators.required
  ]]

});

  submit(){

    if(this.bookForm.valid){

      this.bookService.addBook(this.bookForm.value as any);

      alert("Book Added Successfully");

      this.bookForm.reset();

    }

  }

}