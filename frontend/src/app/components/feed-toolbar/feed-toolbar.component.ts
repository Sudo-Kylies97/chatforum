import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
@Component({selector:'feed-toolbar',standalone:true,imports:[FormsModule],changeDetection:ChangeDetectionStrategy.OnPush,templateUrl:'./feed-toolbar.component.html'})
export class FeedToolbarComponent {readonly search=output<string>();query='';}
