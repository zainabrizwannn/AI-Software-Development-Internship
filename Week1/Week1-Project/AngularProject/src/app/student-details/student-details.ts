import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Student } from '../student';

@Component({
  selector: 'app-student-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './student-details.html',
  styleUrl: './student-details.css'
})
export class StudentDetails {

  @Input() student: Student | null = null;

}