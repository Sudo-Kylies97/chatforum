import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Category } from '../api.service';
@Component({selector:'feed-toolbar',standalone:true,imports:[FormsModule],changeDetection:ChangeDetectionStrategy.OnPush,template:`
<section class="tools"><div><button [class.active]="!selectedCategory()" (click)="filter.emit('')">All</button>@for(c of categories();track c.slug){<button [class.active]="selectedCategory()===c.slug" (click)="filter.emit(c.slug)">{{c.name}}</button>}</div><form (ngSubmit)="search.emit(query)"><input [(ngModel)]="query" name="search" placeholder="Search by meaning…" aria-label="Semantic search"><button>Search</button></form></section>`})
export class FeedToolbarComponent {readonly categories=input.required<Category[]>();readonly selectedCategory=input('');readonly filter=output<string>();readonly search=output<string>();query='';}

