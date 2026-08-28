import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Student} from './Student';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  students: Student[] = [
    { id: 1, name: 'Ali', department: 'CS', marks: 85 },
    { id: 2, name: 'Sara', department: 'IT', marks: 90 },
    { id: 3, name: 'Ahmed', department: 'SE', marks: 80 }
  ];

  selectedStudent: Student | null = null;

  selectStudent(student: Student) {
    this.selectedStudent = student;
  }
}