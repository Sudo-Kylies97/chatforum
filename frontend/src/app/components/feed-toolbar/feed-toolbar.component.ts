import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Category } from '../../api.service';
@Component({selector:'feed-toolbar',standalone:true,imports:[FormsModule],changeDetection:ChangeDetectionStrategy.OnPush,templateUrl:'./feed-toolbar.component.html'})
export class FeedToolbarComponent {readonly categories=input.required<Category[]>();readonly selectedCategory=input('');readonly filter=output<string>();readonly search=output<string>();query='';}
