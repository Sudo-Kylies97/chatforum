import { ChangeDetectionStrategy, Component, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
@Component({selector:'post-composer',standalone:true,imports:[FormsModule],changeDetection:ChangeDetectionStrategy.OnPush,template:`
<section class="composer"><h2>Start a conversation</h2><input [(ngModel)]="title" maxlength="180" placeholder="A clear, specific title" aria-label="Post title"><textarea [(ngModel)]="body" maxlength="10000" placeholder="What would you like the community to consider?" aria-label="Post body"></textarea><div><span class="hint">AI helps categorise your post and assists human moderators.</span><button (click)="submit()" [disabled]="!title.trim()||!body.trim()">Publish post</button></div></section>`})
export class PostComposerComponent { readonly publish=output<{title:string,body:string,done:()=>void}>();title='';body='';submit(){this.publish.emit({title:this.title.trim(),body:this.body.trim(),done:()=>{this.title='';this.body='';}})} }

