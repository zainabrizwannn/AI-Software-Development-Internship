import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { BookList } from './components/book-list/book-list';
import { BookForm } from './components/book-form/book-form';

export const routes: Routes = [

{
path:'',
component:Home
},

{
path:'books',
component:BookList
},

{
path:'add-book',
component:BookForm
}

];