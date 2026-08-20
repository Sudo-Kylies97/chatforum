import { ChangeDetectionStrategy, Component, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
@Component({selector:'post-composer',standalone:true,imports:[FormsModule],changeDetection:ChangeDetectionStrategy.OnPush,templateUrl:'./post-composer.component.html'})
export class PostComposerComponent {readonly publish=output<{title:string,body:string,done:()=>void}>();title='';body='';submit(){this.publish.emit({title:this.title.trim(),body:this.body.trim(),done:()=>{this.title='';this.body='';}})} }
