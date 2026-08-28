import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Student } from '../student';

@Component({
  selector: 'app-student-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './student-list.html',
  styleUrl: './student-list.css'
})
export class StudentList {

  @Input() students: Student[] = [];
  @Input() searchText: string = '';

  @Output() searchTextChange = new EventEmitter<string>();
  @Output() studentSelected = new EventEmitter<Student>();

  get filteredStudents(): Student[] {
    return this.students.filter(student =>
      student.name.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  selectStudent(student: Student) {
    this.studentSelected.emit(student);
  }
}