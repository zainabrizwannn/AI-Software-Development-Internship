import { Component } from '@angular/core';
import { Student } from './student';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  name: string = 'Zainab Akram';
  title: string = 'AI Software Development Intern';
  student: Student = {
  id: 1,
  name: 'Zainab Akram',
  department: 'SE',
  marks: 95
};
}