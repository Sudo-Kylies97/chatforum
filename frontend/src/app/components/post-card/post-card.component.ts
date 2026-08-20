import { ChangeDetectionStrategy, Component, input, output, signal } from '@angular/core';
import { DatePipe, PercentPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Post, User } from '../../api.service';
@Component({selector:'post-card',standalone:true,imports:[DatePipe,PercentPipe,FormsModule],changeDetection:ChangeDetectionStrategy.OnPush,templateUrl:'./post-card.component.html'})
export class PostCardComponent {readonly post=input.required<Post>();readonly user=input<User|null>(null);readonly like=output<Post>();readonly commentAdded=output<{body:string,done:()=>void}>();readonly moderate=output<boolean>();readonly retryAi=output<void>();readonly expanded=signal(false);comment='';submitComment(){this.commentAdded.emit({body:this.comment.trim(),done:()=>{this.comment='';this.expanded.set(true)}})}}
