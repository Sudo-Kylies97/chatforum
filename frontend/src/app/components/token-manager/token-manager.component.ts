import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Token } from '../../api.service';
@Component({selector:'token-manager',standalone:true,imports:[FormsModule],changeDetection:ChangeDetectionStrategy.OnPush,templateUrl:'./token-manager.component.html'})
export class TokenManagerComponent {readonly tokens=input.required<Token[]>();readonly newToken=input('');readonly create=output<string>();readonly revoke=output<number>();name='Assessment integration';}
