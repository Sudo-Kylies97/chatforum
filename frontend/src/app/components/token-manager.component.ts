import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Token } from '../api.service';
@Component({selector:'token-manager',standalone:true,imports:[FormsModule],changeDetection:ChangeDetectionStrategy.OnPush,template:`
<section class="tokens"><h2>Developer access</h2><p>Create revocable API tokens for third-party applications. A new token is shown only once.</p><div><input [(ngModel)]="name" aria-label="Token name"><button (click)="create.emit(name.trim())" [disabled]="!name.trim()">Create token</button></div>@if(newToken()){<code>{{newToken()}}</code>}<ul>@for(token of tokens();track token.id){<li><span><b>{{token.name}}</b> · {{token.prefix}}…</span><button class="quiet" (click)="revoke.emit(token.id)" [disabled]="!!token.revoked_at">{{token.revoked_at?'Revoked':'Revoke'}}</button></li>}</ul></section>`})
export class TokenManagerComponent {readonly tokens=input.required<Token[]>();readonly newToken=input('');readonly create=output<string>();readonly revoke=output<number>();name='Assessment integration';}
