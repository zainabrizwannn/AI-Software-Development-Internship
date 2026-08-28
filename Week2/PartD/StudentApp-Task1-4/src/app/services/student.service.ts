import { Injectable } from '@angular/core';
import { Student } from '../models/student';

@Injectable({
  providedIn: 'root'
})
export class StudentService {

  private students: Student[] = [
    { id: 1, name: 'Ali', email: 'ali@gmail.com' },
    { id: 2, name: 'Ayesha', email: 'ayesha@gmail.com' },
    { id: 3, name: 'Maaz', email: 'maaz@gmail.com' },
    { id: 4, name: 'Eman', email: 'eman@gmail.com' },
    { id: 5, name: 'Alia', email: 'alia@gmail.com' }
  ];

  getStudents(): Student[] {
    return this.students;
  }

  addStudent(student: Student) {
    this.students.push(student);
  }
}