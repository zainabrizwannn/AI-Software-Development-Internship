import { Component } from '@angular/core';
import { Student } from './student';
import { StudentList } from './student-list/student-list';
import { StudentDetails } from './student-details/student-details';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [StudentList, StudentDetails],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {

  title = 'Student Management System';

  students: Student[] = [
  { id: 1, name: 'Maaz', department: 'CS', marks: 88 },
  { id: 2, name: 'Eman', department: 'AI', marks: 91 },
  { id: 3, name: 'Aisha', department: 'SE', marks: 84 },
  { id: 4, name: 'Alia', department: 'IT', marks: 89 },
  { id: 5, name: 'Zainab', department: 'AI', marks: 95 },
  { id: 6, name: 'Ali', department: 'CS', marks: 82 },
  { id: 7, name: 'Sara', department: 'IT', marks: 90 },
  { id: 8, name: 'Ahmed', department: 'SE', marks: 80 },
  { id: 9, name: 'Hassan', department: 'CS', marks: 86 },
  { id: 10, name: 'Fatima', department: 'AI', marks: 93 }
  ];

  selectedStudent: Student | null = null;
  searchText: string = '';

  selectStudent(student: Student) {
    this.selectedStudent = student;
  }
}