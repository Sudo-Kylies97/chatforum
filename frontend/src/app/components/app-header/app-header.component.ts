import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { User } from '../../api.service';
@Component({selector:'app-header',standalone:true,imports:[FormsModule],changeDetection:ChangeDetectionStrategy.OnPush,templateUrl:'./app-header.component.html'})
export class AppHeaderComponent { readonly user=input<User|null>(null); readonly login=output<{username:string,password:string}>(); readonly logout=output<void>(); username='';password=''; submit(){if(this.username.trim()&&this.password){this.login.emit({username:this.username.trim(),password:this.password});this.password='';}} }
