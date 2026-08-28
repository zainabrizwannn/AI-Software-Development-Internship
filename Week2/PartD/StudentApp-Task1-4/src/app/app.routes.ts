import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { StudentList } from './components/student-list/student-list';
import { StudentForm } from './components/student-form/student-form';

export const routes: Routes = [

{
path:'',
component:Home
},

{
path:'students',
component:StudentList
},

{
path:'register',
component:StudentForm
}

];